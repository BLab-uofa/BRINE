import numpy as np
import nimsos.ai_tools
import nimsos.input_tools
import nimsos.output_tools
import csv

class selection():
    """Class of selection

    This class can select the next candidates depending on the AI methods.

    """

    def __init__(self, method, input_file, output_file, num_objectives, num_proposals, num_inputs):
        """Constructor
        
        This function do not depend on robot.

        Args:
            method (str): "RE" or "BO"or "BLOX" or "PDC"
            input_file (str): the file for candidates for AI algorithm
            output_file (str): the file for proposals from AI algorithm
            num_objectives (int): the number of objectives
            num_proposals (int): the number of proposals
            num_inputs (int): the number of fking inputs

        """

        self.method = method
        self.input_file = input_file
        self.output_file = output_file
        self.num_objectives = num_objectives
        self.num_proposals = num_proposals
        self.num_inputs = num_inputs
        
        print(num_inputs)
        
        res = self.module_selection()
        


    def module_selection(self):
        """module selection of preparation input
        
        This function do not depend on robot.

        Returns:
            res (str): True for success, False otherwise.

        """
        res = 'False'
        
        if self.method == "RE":
            res = nimsos.ai_tools.ai_tool_re.RE(self.input_file, self.output_file, 
            self.num_objectives, self.num_proposals).select()
            return res

        if self.method == "PHYSBO":
            res = nimsos.ai_tools.ai_tool_physbo.PHYSBO(self.input_file, self.output_file, 
            self.num_objectives, self.num_proposals).select()
            return res

        if self.method == "PDC":
            res = nimsos.ai_tools.ai_tool_pdc.PDC(self.input_file, self.output_file, 
            self.num_objectives, self.num_proposals).select()
            return res

        if self.method == "BLOX":
            res = nimsos.ai_tools.ai_tool_blox.BLOX(self.input_file, self.output_file, 
            self.num_objectives, self.num_proposals).select()
            return res
        
        if self.method == "GAUCHE":
            res = nimsos.ai_tools.ai_tool_gauche.GAUCHE(self.input_file, self.output_file, 
            self.num_objectives, self.num_proposals).select()
            return res
        
        if self.method == "SMAC3":
            res = nimsos.ai_tools.ai_tool_smac3.SMAC3(self.input_file, self.output_file, 
            self.num_objectives, self.num_proposals, self.num_inputs).select()
            return res
        
        if self.method == "SMAC3_EXPLOIT":
            res = nimsos.ai_tools.ai_tool_smac3_exploiter.SMAC3(self.input_file, self.output_file, 
            self.num_objectives, self.num_proposals, self.num_inputs).select()
            return res
        
        if self.method == "SMAC3_EXPLOIT_REGION":
            res = nimsos.ai_tools.ai_tool_smac3_exploiter_regionbased.SMAC3(self.input_file, self.output_file, 
            self.num_objectives, self.num_proposals, self.num_inputs).select()
            return res

        if self.method == "INDIVIDUALS":
            res = nimsos.ai_tools.ai_tool_individuals.INDIVIDUALS(self.input_file, self.output_file, 
            self.num_objectives, self.num_proposals, self.num_inputs).select()
            return res
            


class preparation_input():
    """Class of preparation input

    This class can create input for robot experiments and star robot experiments.

    """

    def __init__(self, machine, input_file, input_folder, Real_Inputs, Psycho):
        """Constructor
        
        This function do not depend on robot.

        Args:
            machine (str): "STAN" or "NAREE"
            input_file (str): the file for proposals from MI algorithm
            inputFolder (str): the folder where input files for robot are stored

        """

        self.machine = machine
        self.input_file = input_file
        self.input_folder = input_folder
        self.Real_Inputs = Real_Inputs
        self.Psycho = Psycho

        res = self.module_selection()



    def module_selection(self):
        """module selection of preparation input
        
        This function do not depend on robot.

        Returns:
            res (str): True for success, False otherwise.
        """

        if self.machine == "STAN":
            res = nimsos.input_tools.preparation_input_standard.Standard(self.input_file, self.input_folder, self.Real_Inputs).perform(self.Psycho)
            return res

        if self.machine == "NAREE":
            res = nimsos.input_tools.preparation_input_naree.NAREE(self.input_file, self.input_folder).perform()
            return res



class analysis_output():
    """Class of analysis output

    This class can analyze output.

    """

    def __init__(self, machine, input_file, num_objectives, output_folder, Psycho, objectives_info = None):
        """Constructor
        
        This function do not depend on robot.

        Args:
            machine (str): "STAN" or "NAREE"
            input_file (str): the file for proposals from MI algorithm
            output_file (str): the file for candidates which will be updated in this script
            num_objectives (int): the number of objectives
            output_folder (str): the folder where the output files are stored by robot
            objectives_select (dict): the dictionary for objectives selection

        """

        self.machine = machine
        self.input_file = input_file
        self.num_objectives = num_objectives
        self.output_folder = output_folder
        self.objectives_info = objectives_info
        self.Psycho = Psycho

        res = self.module_selection()


    def module_selection(self):
        """module selection of analysis input
        
        This function do not depend on robot.

        Returns:
            res (str): True for success, False otherwise.


        """

        if self.machine == "STAN":
            res = nimsos.output_tools.analysis_output_standard.Standard(self.input_file, self.num_objectives, self.output_folder).perform(self.Psycho)
            return res
        if self.machine == "NAREE":
            res = nimsos.output_tools.analysis_output_naree.NAREE(self.input_file, self.output_file, self.num_objectives, self.output_folder, self.objectives_info).perform()
            return res


# def history(input_file, num_objectives, itt = None, history_file = None):
#     """Containing history results

#     This function do not depend on robot.

#     Args:
#         input_file (str): the file for candidates
#         num_objectives (int): the number of objectives
#         itt (int): the number of step
#         history_file (list[float]): the file for history results

#     Returns:
#         history_file (list[float]): the file for history results (updated)

#     """

#     if history_file is None:

#         arr = np.genfromtxt(input_file, skip_header=1, delimiter=',')
#         arr_train = arr[~np.isnan(arr[:, - 1]), :]

#         X_train = arr_train[:, : - num_objectives].tolist()
#         t_train = arr_train[:, - num_objectives:].tolist()

#         history_file = []

#         if len(X_train) != 0:

#             for i in range(len(X_train)):
#                 history_file.append([0, X_train[i], t_train[i]])

#     else:

#         obs_X = []

#         for i in range(len(history_file)):
#             obs_X.append(history_file[i][1])

#         arr = np.genfromtxt(input_file, skip_header=1, delimiter=',')
#         arr_train = arr[~np.isnan(arr[:, - 1]), :]

#         X_train = arr_train[:, : - num_objectives].tolist()
#         t_train = arr_train[:, - num_objectives:].tolist()

#         for i in range(len(X_train)):

#             if X_train[i] not in obs_X:
#                 history_file.append([itt+1, X_train[i], t_train[i]])

#     return history_file

## OLD update_candidates!
# def update_candidates(input_file, proposals_file, num_objectives):
#     """Update the candidates file with new proposals."""
#     try:
#         with open(input_file, 'a', newline='') as candidates:
#             writer = csv.writer(candidates)
#             with open(proposals_file, 'r') as proposals:
#                 reader = csv.reader(proposals)
#                 next(reader)  # Skip headers
#                 for row in reader:
#                     writer.writerow(row[1:])  # Append proposed conditions without action index
#         return True
#     except Exception as e:
#         print(f"Error updating candidates: {e}")
#         return False

 
    
# def update_candidates(input_file, proposals_file, num_objectives):
#     """Update the candidates file with new proposals or update results for existing inputs."""
#     try:
#         # Read existing candidates
#         try:
#             with open(input_file, 'r') as candidates:
#                 reader = csv.reader(candidates)
#                 data = list(reader)
#         except FileNotFoundError:
#             data = []
#         # Ensure headers exist
#         input_columns = [f'input_{i+1}' for i in range(len(data[0]) - num_objectives)] if data else [f'input_1']
#         output_columns = [f"objective_{i+1}" for i in range(num_objectives)]
#         headers = input_columns + output_columns
#         if not data or data[0] != headers:  # Add headers if missing
#             data = [headers]  # Reset headers to avoid duplication
            
#         # Read proposals
#         with open(proposals_file, 'r') as proposals:
#             reader = csv.reader(proposals)
#             next(reader)  # Skip headers
#             for row in reader:
#                 input_values = row[1:]  # Exclude the "actions" column
#                 result_values = [""] * num_objectives  # Placeholder for results
#                 # Check for duplicate entries
#                 new_row = input_values + result_values
#                 data.append(new_row)
#         # Write updated candidates
#         with open(input_file, 'w', newline='') as candidates:
#             writer = csv.writer(candidates)
#             writer.writerows(data)
#         return True
#     except Exception as e:
#         print(f"Error updating candidates: {e}")
#         return False














