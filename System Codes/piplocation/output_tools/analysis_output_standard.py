import csv
import time
import sys
import math
import csv
import pandas as pd
import os


class Standard():
    """Class of Standard

    This class can perform analysis of outputs from robot.

    """

    def __init__(self, input_file, num_objectives, output_folder):
        """Constructor
        
        This function do not depend on robot.

        Args:
            DELETED (output_file (str): the file for proposals from MI algorithm)
            input_file (str): the file for candidates which will be updated in this script
            num_objectives (int): the number of objectives
            output_folder (str): the folder where the output files are stored by robot

        """

        self.input_file = input_file
        self.num_objectives = num_objectives
        self.output_folder = output_folder


    def perform(self, Psycho):
        """perfroming analysis of output from robots

        This function do not depend on robot.
    
        Returns:
            res (str): True for success, False otherwise.

        """

        global psycho
        psycho = Psycho
        
        print("Start analysis output!")

        res = self.recieve_exit_message(self.output_folder)

        if res == False:
            print("ErrorCode: error in recieve_exit_message function")
            sys.exit()
        
        res, i_List, rows = self.load_data(self.input_file)

        if res == False:
            print("ErrorCode: error in load_data function")
            sys.exit()

        res, r_List = self.extract_objectives(self.output_folder)

        if res == False:
            print("ErrorCode: error in extract_objectives function")
            sys.exit()

        res = self.update_candidate_file(self.input_file, rows, r_List, i_List)

        if res == False:
            print("ErrorCode: error in update_candidate_file function")
            sys.exit()

        # self.log_psycho()
        
        print("Finish analysis output!")

        return "True"



    def load_data(self, input_file):
        """
        Locate the last row whose objective column is empty/NaN
        and return that row so it can be updated with the real result.
        Returns
        -------
        res        : bool
        target_row : list[str]       – the row to overwrite
        rows       : list[list[str]] – full CSV content
        """
        try:
            import pandas as pd
            df = pd.read_csv(input_file, dtype=str)   # keep cells as strings
            obj_col = df.columns[-1]                  # objective = last column
            # boolean mask for rows whose objective cell is blank or NaN
            mask_empty = df[obj_col].isna() | (df[obj_col].str.strip() == "")
            if not mask_empty.any():
                raise ValueError("No pending experiment row (objective NaN) found.")
            # index of the last such row
            target_idx = mask_empty[::-1].idxmax()
            target_row = df.iloc[target_idx].tolist()
            rows = df.values.tolist()                 # list‑of‑lists for updater
            res  = True
            # store index for updater (optional: as an attribute)
            self._target_idx = target_idx
            
        except Exception as e:
            print("load_data error:", e)
            res, target_row, rows = False, None, None
            
        return res, target_row, rows



    def recieve_exit_message(self, output_folder):
        """Recieving exit message from machine

        This function DEPENDS on robot.

        Args:
            output_folder (str): the folder where the results by machine are stored

        Returns:
            res (bool): True for success, False otherwise.

        """

        try:
            filepath = output_folder + "/outputend.txt"

            while not(os.path.isfile(filepath)):
                time.sleep(10)

            os.remove(filepath)

            res = True


        except:
            res = False

        return res



    def extract_objectives(self, output_folder):    
        """Extracting objective values from output files by robot

        This function DEPENDS on robot.

        Args:
            num_objectives (int): the number of objectives
            output_folder (str): the folder where the results by machine are stored
            p_List (list[float]): the list of proposals

        Returns:
            res (bool): True for success, False otherwise.
            r_List (list[float]): the list of objectives

        """

        try:
            filepath = output_folder + "/results.csv"
            with open(filepath) as inf:
                reader = csv.reader(inf)
                r_List = next(reader)
                  
            res = True

        except:
            res = False

        return res, r_List


    def update_candidate_file(self, input_file, rows_unused, r_List_unused,
                          i_List_unused):
        """Updating candidates
        This function does not depend on robot.
        Args:
            num_objectives (int): the number of objectives
            DELETED (output_file)
            r_List (list[float]): the list of objectives
        Returns:
            res (bool): True for success, False otherwise.
        """
        global psycho
        
        try:
            df = pd.read_csv(input_file)
            
            obj_col = df.columns[-1]                        # last column
            mask = df[obj_col].isna() | (df[obj_col].astype(str).str.strip() == "")
            if not mask.any():
                raise ValueError("No placeholder row (NaN) found.")
            
            target_idx = mask[::-1].idxmax()                # last NaN row
            df.at[target_idx, obj_col] = r_List_unused[0]   # write result
            df.to_csv(input_file, index=False)
            print(f"Result saved to row {target_idx+1} in {input_file}")
            return True
        
        except Exception as e:
            print(f"Error updating candidates: {e}")
            return False
        
    # def log_psycho(self):
    #     psycho_file = os.path.join(self.output_folder, "psychos.csv")
    #     try:
    #         with open(psycho_file, 'a', newline='') as f:
    #             writer = csv.writer(f)
    #             writer.writerow([self.psycho])
    #         print(f"Psycho {self.psycho} was saved.")
    #     except Exception as e:
    #         print(f'Error in saving psycho: {e}')

