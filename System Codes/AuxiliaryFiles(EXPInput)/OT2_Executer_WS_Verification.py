import requests
import json
import asyncio
import websockets
import time
from websockets.exceptions import WebSocketException, ConnectionClosedError

def main():
    
    
    notebook_url = 'http://169.254.177.16:48888/api/sessions'
    headers = {'Content-Type': 'application/json'}
    session_data = {
        "kernel": {"name": "python3"},
        "name": "NIMS_OS_name",
        "path": "NIMS_OS.ipynb",
        "type": "notebook"
    }

    response = requests.post(notebook_url, headers=headers, data=json.dumps(session_data))
    session_info = response.json()
    if 'kernel' not in session_info:
        print("Error: Kernel information not found in the response.")
        exit()
        
    kernel_id = session_info['kernel']['id']
    ws_url = f"ws://169.254.177.16:48888/api/kernels/{kernel_id}/channels"


    try:
        with open('./EXPInput/UPDATES.json', 'r') as conf_file:
            conf = json.load(conf_file)
    except Exception as e:
        print('couldnt locate UPDATES')
    
    psycho = conf['psycho']
    suggest_ratios = conf['suggest_ratios']
    real_salt_no = conf['real_salt_no']
    
    

    def shutdown_kernel(kernel_id):
        shutdown_url = f"http://169.254.177.16:48888/api/kernels/{kernel_id}"
        requests.delete(shutdown_url)
        print("Kernel has been shut down.")

    async def send_message_via_ws(ws_url, code, message_name):
        try:
            # Log start of the connection attempt
            print(f"Starting WebSocket execution for {message_name}...")
            async with websockets.connect(ws_url) as websocket:
                # Prepare the message with the provided code
                msg = {
                    "header": {
                        "msg_id": "execute_request",
                        "username": "Reza",
                        "session": "",
                        "msg_type": "execute_request",
                        "version": "5.3"
                    },
                    "parent_header": {},
                    "metadata": {},
                    "content": {
                        "code": code,
                        "silent": False,
                    }
                }
                # Send the message
                await websocket.send(json.dumps(msg))
                print(f"Message sent for {message_name}. Waiting for response...")
                # Listen for responses until execution is fully completed
                while True:
                    response = await websocket.recv()
                    print(f"{message_name} response: {response}")
                    # Check for the "idle" state indicating completion
                    if '"execution_state": "idle"' in response:
                        print(f"{message_name} execution completed, closing WebSocket.")
                        break
                await websocket.close()
                print(f"WebSocket closed for {message_name}.")
        except (WebSocketException, ConnectionClosedError) as e:
            print(f"WebSocket error occurred during {message_name}: {e}")  
    
    protocol_code_first = f"""   
        cycle_no = {psycho}
        f_VOL_string = {suggest_ratios}
        real_salt_no= {real_salt_no}
        WELLS_PER_PLATE = 96
        ROWS_PER_COL = 8
        
        ### Tip CONSTANTS
        TIPS_PER_RACK = 96
        
        import opentrons.execute
        protocol = opentrons.execute.get_protocol_api('2.20')
        from opentrons.types import Point, Location
        protocol.home()
        
        # Load pipettes and labware
        Lpipette = protocol.load_instrument('p300_single_gen2', 'left')
        Rpipette = protocol.load_instrument('p1000_single_gen2', 'right')
        reservoir = protocol.load_labware("nest_12_reservoir_15ml", 7)
        reservoir_c = protocol.load_labware("nest_12_reservoir_15ml", 10)
        reservoir_f = protocol.load_labware("nest_12_reservoir_15ml", 11)
    
        
        def get_tip_rack_and_address(tip_no):
            # tip_rack_order = ['9', '6', '5', '4', '3', '2', '1']  # Deck slots in usage order (as strings)
            tip_rack_order = ['9', '9', '6', '3', '2', '1', '4', '9']  # Deck slots in usage order (as strings)
            ROWS_PER_COL = 8
            # Identify which tip rack this tip belongs to
            rack_index = tip_no // TIPS_PER_RACK
            
            
            if rack_index >= len(tip_rack_order):
                raise ValueError("Tip number exceeds available tip racks.")
                
            deck_slot = tip_rack_order[rack_index]
            
            # Load tip rack if not already present using string keys
            if not protocol.deck.get(deck_slot):
                Tips = protocol.load_labware('opentrons_96_tiprack_300ul', deck_slot)
            else:
                Tips = protocol.deck[deck_slot]

            position_in_rack = tip_no % TIPS_PER_RACK
            row = position_in_rack % ROWS_PER_COL
            col = position_in_rack // ROWS_PER_COL
            tip_address = chr(65 + row) + str(col + 1)
            return Tips, tip_address

            
        def get_plate_address(psycho: int):
            # Return the NEST plate loaded in the correct deck slot *and* a handy
            # (rows, cols) matrix for well addressing.
        
            # Parameters
            # ----------
            # psycho : int
            #     Experiment counter starting at 1.
        
            # Returns
            # -------
            # plate        : Labware
            #     The NEST 96‑well plate object (loaded or retrieved from the deck).
            # plate_rows   : List[List[Well]]
            #     Matrix‑style handle for addressing:  plate_rows[row][col]
            
            plate_order = ['8', '5']
        
            plate_index = (psycho -1) // WELLS_PER_PLATE
        
            if plate_index >= len(plate_order):
                raise ValueError(
                    "Test cells exceed the available NEST plates. "
                    "Add more plates or cut down the experiment count."
                )
        
            deck_slot = plate_order[plate_index]
        
            if not protocol.deck.get(deck_slot):     # Load the plate only once – subsequent calls will reuse the cached object
                plate = protocol.load_labware('nest_96_wellplate_2ml_deep', deck_slot)
            else:
                plate = protocol.deck[deck_slot]

            
            plate.set_offset(x=-0.5, y=1.5, z=0.0)
            plate_rows = plate.rows()
            return plate, plate_rows


        
        # Main Protocol STARTS HERE !!!
        _, Row = get_plate_address(cycle_no)
        
        # Initial and Final molarities       
        i_mol = [5, 4, 4, 2, 0.5] ## ZnCl2, KCl, NH4Cl, NaCl, EMICl 
        dimension = len(i_mol)
        
        pos_in_plate = (cycle_no - 1) % WELLS_PER_PLATE
        row_no = pos_in_plate % ROWS_PER_COL       # 0–7
        col_no = pos_in_plate // ROWS_PER_COL      # 0–11
        
        tip_no = (cycle_no-1) * (real_salt_no + 1)
        target_well = Row[row_no][col_no]
        
        vol = [float(x) for x in f_VOL_string]
        w_vol = 330 - sum(vol)
        
        # Mixing begins here
        if w_vol >= 20:
        
            t = 0  # counter of tips
                
            for i in range(dimension+1):
                j = i + 1  # counter of reserv cells. USED TO BE 2*i+1

                
                if i == dimension:
                    tips, tip_add = get_tip_rack_and_address(tip_no + t)
                    Lpipette.pick_up_tip(tips[tip_add])
                    Lpipette.transfer(w_vol,  reservoir["A12"], target_well, new_tip='never', mix_after=(4, 150))
                    Lpipette.move_to(target_well.top(100))
                    Lpipette.drop_tip()
                else:
                    if vol[i] >= 20:
                        tips, tip_add = get_tip_rack_and_address(tip_no + t)
                        Lpipette.pick_up_tip(tips[tip_add])
                        Lpipette.transfer(vol[i], reservoir['A'+str(j)], target_well, new_tip='never')
                        Lpipette.move_to(target_well.top(100))
                        Lpipette.drop_tip()
                        t += 1
                
                
        elif w_vol < 20 and w_vol > 0:
            tips, tip_add = get_tip_rack_and_address(tip_no)
            Lpipette.pick_up_tip(tips[tip_add])
            Lpipette.transfer(150,  reservoir["A12"], target_well, new_tip='never')
            Lpipette.transfer(150 - w_vol, target_well, reservoir["A11"], new_tip='never')
            Lpipette.move_to(reservoir["A11"].top(100))
            Lpipette.drop_tip()
            
            t = 0
            for i in range(dimension):
                j = i + 1
                
                if vol[i] >= 20:
                    tips, tip_add = get_tip_rack_and_address(tip_no + t + 1)
                    Lpipette.pick_up_tip(tips[tip_add])
                    if i == dimension-1:
                        Lpipette.transfer(vol[i], reservoir['A'+str(j)], target_well, new_tip='never', mix_after=(4, 150))
                    else:
                        Lpipette.transfer(vol[i], reservoir['A'+str(j)], target_well, new_tip='never')
                    Lpipette.move_to(target_well.top(100))
                    Lpipette.drop_tip()
                    t += 1
                
        else:  ## No or almost no water needed to add
            t = 0
            for i in range(dimension): 
                j = i + 1
                
                if i == dimension-1:
                    tips, tip_add = get_tip_rack_and_address(tip_no + t)
                    Lpipette.pick_up_tip(tips[tip_add])
                    Lpipette.transfer(vol[i], reservoir['A'+str(j)], target_well, new_tip='never', mix_after=(4, 150))
                    Lpipette.move_to(target_well.top(100))
                    Lpipette.drop_tip()
                    
                else:
                    if vol[i] >= 20:
                        tips, tip_add = get_tip_rack_and_address(tip_no + t)
                        Lpipette.pick_up_tip(tips[tip_add])
                        Lpipette.transfer(vol[i], reservoir['A'+str(j)], target_well, new_tip='never')
                        Lpipette.move_to(target_well.top(100))
                        Lpipette.drop_tip()
                        t += 1
                        
                
                
        
        # Rpipette; Gamry time!
        well_location = target_well.bottom(69)
        Rpipette.move_to(well_location)
        protocol.delay(60)

        """        
    
    # Send protocol code
    print("Starting first WebSocket execution...")
    asyncio.get_event_loop().run_until_complete(send_message_via_ws(ws_url, protocol_code_first, 'protocol_code_first'))
    print("First WebSocket execution completed.")
    time.sleep(0.5)


    
    # Execute the Gamry test
    try:

        gamry_exec_path = './EXPInput/Gamry_CircuitFit_PyImpSpec3R.py'
        exec_globals = {
            "__name__":"__main__",
            "__file__":gamry_exec_path,
        }
        with open(gamry_exec_path, 'r') as file:
            code = file.read()
        exec(code, exec_globals)
        
        print("Gamry completed!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(0.5)

    
    continuation_code = """
    Rpipette.home()
    tc0= reservoir_c['A1']
    tc1= reservoir_c['A2']
    tc2= reservoir_c['A3']
    tc3= reservoir_c['A4']
    tc5= reservoir_c['A6']
    tc6= reservoir_c['A7']
    tc7= reservoir_c['A8']
    tc8= reservoir_c['A9']
    tc12= reservoir_c['A12']
    
    if cycle_no < 60:
        tcs = [tc0,tc1,tc2,tc3]
    else:
        tcs = [tc5,tc6,tc7,tc8]
        
    target_dry = reservoir_f['A7']
    
    Rpipette.move_to(tcs[0].bottom(z=86))
    for cnt in range(len(tcs)):
        for _ in range(4):  ## Swinging 4 times
            Rpipette.move_to(tcs[cnt].bottom(z=85).move(Point(y=+22)))
            Rpipette.move_to(tcs[cnt].bottom(z=85).move(Point(y=-22)))
            protocol.delay(0.1)
        Rpipette.move_to(tcs[cnt].bottom(z=110))
    
    
    Rpipette.move_to(tc12.bottom(z=86))
    Rpipette.move_to(tc12.bottom(z=86).move(Point(y=+14)))
    Rpipette.move_to(tc12.bottom(z=86).move(Point(y=-14)))
    protocol.delay(0.05)
    Rpipette.move_to(tc12.bottom(z=86).move(Point(y=+14)))
    Rpipette.move_to(tc12.bottom(z=86).move(Point(y=-14)))
    protocol.delay(0.05)
    Rpipette.move_to(tc12.bottom(z=110))

    Rpipette.move_to(target_dry.bottom(z=78).move(Point(y=+45)))
    protocol.delay(10)

    """
    
    # Send continuation code
    print("Starting continuation WebSocket execution...")
    asyncio.get_event_loop().run_until_complete(send_message_via_ws(ws_url, continuation_code, 'continuation_code'))
    print("Continuation WebSocket execution completed.") 
    
    shutdown_kernel(kernel_id)

if __name__ == "__main__":
    main()
