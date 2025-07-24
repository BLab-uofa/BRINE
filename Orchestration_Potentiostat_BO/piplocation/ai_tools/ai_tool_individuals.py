import sys
import os
import pandas as pd
import numpy as np


class INDIVIDUALS:
    """Class to select the next candidates based on a predefined resource file."""
    def __init__(self, input_file, output_file, num_objectives, num_proposals, num_inputs):
        """Constructor
        Args:
            input_file (str): the file for candidates
            output_file (str): the file for proposals from the algorithm (unused in this context)
            num_objectives (int): the number of objectives
            num_proposals (int): the number of proposals
            num_inputs (int): the number of inputs
        """
        self.input_file = input_file  # 'candidates.csv'
        self.output_file = output_file
        self.num_objectives = num_objectives
        self.num_proposals = num_proposals
        self.num_inputs = num_inputs
        self.candidates_resource_file = 'candidates_resource.csv'
        
        # Check if candidates_resource.csv exists
        if not os.path.exists(self.candidates_resource_file):
            print(f"Error: Required file '{self.candidates_resource_file}' not found.")
            sys.exit(1)
        
        # Ensure input_file exists with appropriate headers
        self._ensure_input_file_exists()
    
    
    def _ensure_input_file_exists(self):
        """Ensure the input file exists with appropriate headers."""
        if not os.path.exists(self.input_file):  # Check if the file exists
            # Read headers from candidates_resource.csv
            resource_data = pd.read_csv(self.candidates_resource_file)
            # Use only columns up to num_inputs
            input_columns = resource_data.columns.tolist()[:self.num_inputs]
            output_columns = [f'objective_{i + 1}' for i in range(self.num_objectives)]
            columns = input_columns + output_columns
            # Create an empty DataFrame with these columns and save to input_file
            pd.DataFrame(columns=columns).to_csv(self.input_file, index=False)
            print(f"Created input file '{self.input_file}' with headers: {columns}")



    def load_data(self):
        """Load data from candidates_resource.csv and input_file."""
        # Load candidates_resource.csv
        resource_data = pd.read_csv(self.candidates_resource_file)
        # Ensure resource_data has at least num_inputs columns
        if resource_data.shape[1] < self.num_inputs:
            print(f"Error: '{self.candidates_resource_file}' does not have enough columns.")
            sys.exit(1)
        # Load input_file (candidates.csv)
        input_data = pd.read_csv(self.input_file)
        return resource_data, input_data
    
    
    
    def select(self):
        """Select the next candidate from candidates_resource.csv and write to input_file."""
        print("Start of selection process!")
        resource_data, input_data = self.load_data()
        # Determine the next index to read from resource_data
        next_index = len(input_data)
        # Check if resource_data has enough rows
        if next_index >= len(resource_data):
            print("No more candidates available in resource file.")
            return False
        # Extract the row at next_index
        selected_row = resource_data.iloc[next_index]
        # Extract inputs up to num_inputs
        inputs = selected_row.iloc[:self.num_inputs].tolist()
        print(f"Selected inputs: {inputs}")
        # Write the results
        self.write_results(inputs)
        print("Selection of proposals ended!")
        return True
    
    
    def write_results(self, inputs):
        """Append the selected inputs to input_file with empty objectives."""
        # Prepare the row to append
        objectives = [np.nan for _ in range(self.num_objectives)]
        row = inputs + objectives
        # Load current data
        data = pd.read_csv(self.input_file)
        # Append the row
        data.loc[len(data)] = row
        # Save back to input_file
        data.to_csv(self.input_file, index=False)
        print(f"Appended inputs to '{self.input_file}': {inputs}")