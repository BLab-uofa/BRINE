import os
import numpy as np
from pandas import DataFrame
import pandas as pd
import matplotlib.pyplot as plt
import time
from pygamry.dtaq import get_pstat, DtaqOcv, DtaqReadZ
import json
from pyimpspec import Circuit, DataSet, FitResult, parse_data, fit_circuit, parse_cdc


def main():

    ## IN ORDER TO GET THE CYCLE VALUES
    try:
        with open('./EXPInput/UPDATES.json', 'r') as conf_file:
            conf = json.load(conf_file)
    except Exception as e:
        print('couldnt locate UPDATES')
    psycho = conf['psycho']

    data_path = './EXPOutput' #  os.pardir + '/EXPOutput'
    empty_verif_text_name = "outputend.txt"
    suffix = 'NIMS'

    ocp_duration = 25
    ocp_sample_period = 1
    eis_max_freq = 1.2e6
    eis_min_freq = 5e3
    eis_ppd = 15
    z_guess = 30
    AC_RMS = 0.01 # mV


    if os.path.exists(data_path + '/' + empty_verif_text_name):
        os.remove(data_path + '/' + empty_verif_text_name)

    # Ensure data directory exists
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    pstat = get_pstat()

    # Configure OCV
    # Write to file every minute
    ocv = DtaqOcv(write_mode='interval', write_interval=int(60 / ocp_sample_period))

    # Configure EIS
    # Write continuously
    eis = DtaqReadZ(mode='pot', readzspeed='ReadZSpeedNorm', write_mode='continuous')

    sigmas = []
    
    for i in range(3): # Repeat EIS 3 times
        
        # Run OCV
        print(f'Running OCV - iter {i+1}')
        ocv_file = os.path.join(data_path, f'OCV_{psycho}' + f'{suffix}.DTA')
        ocv.run(pstat, ocp_duration, ocp_sample_period, show_plot=True, result_file=ocv_file)
        print('OCV done\n')

        plt.close()
        time.sleep(1)

        # Get measured OCV for EIS
        V_oc = np.mean(ocv.dataframe['Vf'].values[-10:])  # average last 10 values
        # print('OCV: {:.3f} V'.format(V_oc))

        # Run EIS
        # Get frequencies to measure
        num_decades = np.log10(eis_max_freq) - np.log10(eis_min_freq)
        num_freq = int(eis_ppd * num_decades) + 1
        eis_freq = np.logspace(np.log10(eis_max_freq), np.log10(eis_min_freq), num_freq)
        V_dc = V_oc
    
        print(f'Running EIS - iter {i+1}')
        eis_file = os.path.join(data_path, f'EIS_{psycho}' + f'_{i}'+ f'{suffix}.DTA')
        eis.run(pstat, eis_freq, V_dc, AC_RMS, z_guess, timeout=60,
                show_plot=True, plot_interval=1, plot_type='all',
                result_file=eis_file)
        print('EIS done\n')

        plt.close()
        time.sleep(5)
    
        ### THIS TRY BLOCK WILL BE FOR DATA PARSE TO FIND R (RESISTANCE)
        try:
            with open(eis_file, 'r'):
                data: DataSet = parse_data(eis_file)[0]

            circuit: Circuit = parse_cdc("RQ")
            fit: FitResult = fit_circuit(circuit, data)
            fit.circuit.to_sympy()
            df: DataFrame = fit.to_parameters_dataframe(running=True)
            R = df.loc[df['Parameter'] == 'R', 'Value'].values[0] 
            # print(f'R value found in iter {i}: {R}')
            
        except Exception as e:
            print(f'Couldnt access EIS path/res: {e}')
        
    ### FINDING CONDUCTIVITY BEGINS HERE

        Kcell = 164.04933518 # Kcell = 128.80553916323296  
        alpha =  1 # calibration factor(s)
        sigma = alpha * Kcell / R
        sigmas.append(sigma)

    # Save sigma to THE CSV file
    avg_sigma = np.mean(sigmas)
    save_path = os.path.join(data_path, 'results.csv')
    pd.DataFrame([avg_sigma]).to_csv(save_path, index=False, header=False)
    print(f"Avg Sigma value saved to {save_path}")

    cat_save_path = os.path.join(data_path, 'results_cat.csv')
    pd.DataFrame(sigmas).to_csv(cat_save_path, mode='a', index=False, header=False)

    # os.makedirs(data_path, exist_ok=True)
    
    try:
        file_pathh = os.path.join(data_path, empty_verif_text_name)
        with open(file_pathh, 'w'):
            pass
        print ('Gamry fitting done!')
    except Exception as e:
        print(f"Error: {e}")
        
        
if __name__ == "__main__":
    main()
