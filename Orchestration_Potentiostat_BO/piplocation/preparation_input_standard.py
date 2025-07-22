import csv
import sys
import json
# import os
#import subprocess
#import time
#import pathlib
# sys.path.append('C:/Users/Blab2/Desktop/NIMSOS_base')
# from globals import cycle_no

# print('CycleNo in input-class: ', cycle_no)
# print(f"py lib path: {sys.path}")


class Standard():
    """Class of Standard

    This class can create input file for robot experiments and start the robot experiments.

    """

    def __init__(self, input_file, input_folder, Real_Inputs):
        """Constructor
        
        This function do not depend on robot.

        Args:
            input_file (str): the file for proposals from MI algorithm
            input_folder (str): the folder where input files for robot are stored

        """

        self.input_file = input_file
        self.inputFolder = input_folder
        self.Real_Inputs = Real_Inputs



    def perform(self, Psycho):
        """perfroming preparation input and starting robot experiments 

        This function do not depend on robot.
    
        Returns:
            res (str): True for success, False otherwise.

        """
        global psycho
        psycho = Psycho
        
        print("Start preparation input!")

        res, p_List = self.load_data(self.input_file)

        if res == False:
            print("ErrorCode: error in load_data function")
            sys.exit()

        res = self.make_machine_file(p_List,self.inputFolder, self.Real_Inputs)

        if res == False:
            print("ErrorCode: error in make_machine_file function")
            sys.exit()

        res = self.send_message_machine(self.inputFolder)

        if res == False:
            print("ErrorCode: error in send_message_machine function")
            sys.exit()


        print("Finish preparation input!")

        return "True"



    def load_data(self, input_file):
        """Loading proposals

        This function do not depend on robot.
    
        Args:
            input_file (str): the file for proposals from AI algorithm

        Returns:
            res (bool): True for success, False otherwise.
            p_List (list[float]): the list of proposals

        """

        p_List = []
        try:
            with open(input_file) as inf:
                reader = csv.reader(inf)
                last_row = None
                
                for row in reader:
                    last_row = row
            
            p_List = [last_row]
                
            res = True

        except:
            res = False

        return res, p_List 



    def make_machine_file(self, p_List, inputFolder, Real_Inputs):
        """Making input files for robot

        This function DEPEND on robot.

        Args:
            p_List (list[float]): the list of proposals 
            inputFolder (str): the folder where the input files for robot are stored

        Returns:
            res (bool): True for success, False otherwise.

        """

        res = False

        try:
            
            global psycho
            
            
            suggest_ratios = p_List[-1][0:-1]  # Since the last one is NaN
            print('SHT! we are at make_machine')
            
            # UPDATES.CONF Formation
            conf = {
                "suggest_ratios": suggest_ratios,
                "psycho": psycho,
                "real_salt_no": Real_Inputs
            }
            
            conf_path = inputFolder + "/UPDATES.json"
            with open(conf_path , 'w') as conf_file:
                json.dump(conf, conf_file)
                
            res = True  

        except Exception as e:
            print(f"Error: {e}")
            res = False

        return res


    def send_message_machine(self, inputFolder):
        
        """Sending a message to start the robot
    
        This function DEPENDS on robot.
    
        Args:
            inputFolder (str): the folder where the input files for robot are stored
    
        Returns:
            res (bool): True for success, False otherwise.
    
        """
        res = False
        print('SHT! we are at send_message_machine')
    
        try:
            # Path to the WebSocket protocol script
            protocol_exec_path = inputFolder + "/OT2_Executer_WS_Verification.py"
            
            exec_globals = {
                "__name__":"__main__",
                "__file__":protocol_exec_path,
            }
            with open(protocol_exec_path, 'r') as file:
                code = file.read()
                
            exec(code, exec_globals)   

            res = True
            
    
        except Exception as e:
            res = False
            print(f"Error: {e}")
    
        return res


