import sys
import os
import random
import pandas as pd
import numpy as np
from ConfigSpace import ConfigurationSpace, UniformIntegerHyperparameter, Configuration

from smac import Scenario
from smac.facade.hyperparameter_optimization_facade import HyperparameterOptimizationFacade
from smac.runhistory.runhistory import RunHistory
from smac.runhistory.enumerations import StatusType
from smac.runhistory.dataclasses import TrialValue
from smac.acquisition.function import LCB 
from smac.acquisition.function import EI
from smac.initial_design.abstract_initial_design import AbstractInitialDesign
from smac.initial_design import SobolInitialDesign
from smac.utils.logging import get_logger

from typing import List
import csv

class SMAC3():
    """Class of SMAC3

    This class can select the next candidates by Bayesian optimization based on SMAC3 package.

    """
    
    def __init__(self, input_file, output_file, num_objectives, num_proposals, num_inputs):
        """Constructor
        
        This function do not depend on robot.
        Args:
            input_file (str): the file for candidates for MI algorithm
            output_file (str): the file for proposals from MI algorithm
            num_objectives (int): the number of objectives
            num_proposals (int): the number of proposals
            num_inputs (int): the number of the FUCKINGGGG INPUTSSS!!!
        """
        
        self.input_file = input_file
        self.num_objectives = num_objectives
        self.output_file = output_file
        self.num_proposals = num_proposals
        self.num_inputs = num_inputs
        self.max_sum = 330  # Constraint
        
        
        # self.min_input_value = 20
        # self.max_input_value = self.max_sum - self.min_input_value * (self.num_inputs - 1)  # Maximum input value
        
        self.min_input_values = [20] * self.num_inputs
        self.min_input_values[0] = 33
        total_min = sum(self.min_input_values)
        self.max_input_values = [self.max_sum - (total_min - m) for m in self.min_input_values]
        
        
        
        

        self._ensure_input_file_exists()
        
    def _ensure_input_file_exists(self):
        """Ensure the input file exists with appropriate headers."""
        if not os.path.exists(self.input_file):  # Check if the file exists
            # Construct the headers dynamically based on num_inputs and num_objectives
            input_columns = [f'input_{i + 1}' for i in range(self.num_inputs)]
            print(["iunpouts in BO: ",self.num_inputs])
            
            output_columns = [f'objective_{i + 1}' for i in range(self.num_objectives)]
            columns = input_columns + output_columns
            pd.DataFrame(columns=columns).to_csv(self.input_file, index=False)
            print(f"Created input file '{self.input_file}' with headers: {columns}")
            
            
    def _append_row(self, inputs, objective_value):
        """
        Append a single row to candidates.csv.
        Parameters
        ----------
        inputs : list[int]
            The proposed input values.
        objective_value : float or np.nan
            The value to store in the objective column.
            Use np.nan for 'to‑be‑measured‑later', or a large
            negative number for penalties.
        """
        data, _ = self.load_data()          # always reload to avoid races
        row = inputs + [objective_value]
        data.loc[len(data)] = row
        data.to_csv(self.input_file, index=False)
        
    
    def load_data(self):
        """Load candidates from CSV file."""
        try:
            data = pd.read_csv(self.input_file)

            valid_data = data.dropna()  # Drop rows with NaN values
            has_prior_data = not valid_data.empty

            # Log the data being used for debugging
            print(f"Valid Data for SMAC:\n{valid_data}")
    
        except FileNotFoundError:# Create an empty file if it doesn't exist

            input_columns = [f'input_{i + 1}' for i in range(self.num_inputs)]
            output_columns = [f'objective_{i + 1}' for i in range(self.num_objectives)]
            columns = input_columns + output_columns
            data = pd.DataFrame(columns=columns)
            data.to_csv(self.input_file, index=False)
            has_prior_data = False
        return data, has_prior_data

    def objective_function(self, config, seed=None):
        """
        Objective function that penalizes configurations violating the sum constraint.
        """
        inputs = [config[f"input_{i + 1}"] for i in range(self.num_inputs)]
        if sum(inputs) > self.max_sum:
            return 1e2  # Penalize if constraint is violated
        else:
            return -100  # Return zero cost for valid configurations
        
    def run_smac(self):
        """
        Start a fresh SMAC instance, replay all previous evaluations
        from candidates.csv, then keep asking until a *feasible*
        configuration (sum(inputs) ≤ self.max_sum) is obtained.
        The infeasible proposals encountered on the way are
        penalised (cost = 1e12) and written to candidates.csv with
        objective = -1e12, so future SMAC runs remember them.
        Returns
        -------
        proposed_inputs : list[int]
            The first feasible input set, ready for the robot.
        """
        data, has_prior_data = self.load_data()
        row_count = len(data)
        
        if row_count % 4 == 0:
            acq = LCB(beta=1.2)
            print("acq ALERT: Exploring...")
        else:
            acq = EI(xi=0)
            print("acq ALRET: Balancing explore-exploit...")
            

        cs = ConfigurationSpace()
        # for i in range(self.num_inputs):
        #     cs.add(
        #         UniformIntegerHyperparameter(
        #             f"input_{i + 1}",
        #             self.min_input_value,
        #             self.max_input_value
        #         )
        #     )
        for i in range(self.num_inputs):
            cs.add(
                UniformIntegerHyperparameter(
                    f"input_{i+1}",
                    self.min_input_values[i],
                    self.max_input_values[i]
                )
            )
        
        

        scenario = Scenario(
            cs,
            deterministic=True,
            n_trials=100,
            seed=random.randint(0, 2**32 - 1),
        )
        smac = HyperparameterOptimizationFacade(
            scenario=scenario,
            target_function=self.objective_function,   # penalty!
            acquisition_function=acq,
            initial_design=ConstrainedRandomInitialDesign(
                scenario=scenario,
                num_inputs=self.num_inputs,
                max_sum=self.max_sum,
            ),
        )
        # ---------- 4. replay prior history ----------
        if has_prior_data:
            rh = RunHistory()
            for _, row in data.iterrows():
                cfg = {f"input_{i+1}": int(row[f"input_{i+1}"])
                       for i in range(self.num_inputs)}
                cost = -float(row['objective_1'])
                rh.add(Configuration(cs, values=cfg),
                       cost=cost,
                       time=0.0,
                       status=StatusType.SUCCESS,
                       seed=0)
            smac.runhistory.update(rh)
        # ---------- 5. ask‑check‑tell loop ----------
        max_attempts = 50           # safety valve
        attempts     = 0
        while True:
            attempts += 1
            trial  = smac.ask()
            cfg    = trial.config
            inputs = [cfg[f"input_{i+1}"] for i in range(self.num_inputs)]
            if sum(inputs) <= self.max_sum:          # :white_check_mark: feasible
                print(f"Feasible proposal: {inputs}")
                # store inputs with NaN → orchestrator will overwrite
                self._append_row(inputs, np.nan)
                return inputs
            # :no_entry_sign: infeasible: penalise & persist
            penalty_cost      = 1e2    # for SMAC (it minimises cost)
            penalty_objective = -1e2   # for CSV (we maximise objective)
            
            penalty_value = TrialValue(
                cost=penalty_cost,
                time = 0.0,
                status = StatusType.CRASHED,
            )
            smac.tell(trial, penalty_value)
            
            self._append_row(inputs, penalty_objective)
            print(f"Infeasible proposal {inputs} recorded with penalty.")
            if attempts >= max_attempts:
                raise RuntimeError("Too many infeasible proposals in a row.")


    def write_results(self, inputs):
        """Writes the proposed inputs to candidates.csv with empty objective."""
        data, _ = self.load_data()
        row = inputs + [np.nan]  # Combine inputs with an empty result
        data.loc[len(data)] = row  # Add new row
        data.to_csv(self.input_file, index=False)

    def select(self):
        
        print("Start of SMAC3!")
        
        proposed_inputs = self.run_smac()
        print(f"Proposed inputs: {proposed_inputs}")
        print("Selection of proposals ended!")
        
        return True
    
    
class ConstrainedRandomInitialDesign(AbstractInitialDesign):
    def __init__(self, scenario, num_inputs, max_sum, **kwargs):
        super().__init__(scenario=scenario, **kwargs)
        self.num_inputs = num_inputs
        self.max_sum = max_sum
        self.logger = get_logger(self.__class__.__name__)

    def _select_configurations(self) -> List[Configuration]:
        configurations = []
        max_iterations = 1000 * self._n_configs  # To prevent infinite loops
        iterations = 0
        while len(configurations) < self._n_configs and iterations < max_iterations:
            config = self._configspace.sample_configuration()
            inputs = [config[f"input_{i + 1}"] for i in range(self.num_inputs)]
            if sum(inputs) <= self.max_sum:
                configurations.append(config)
            iterations += 1
        if len(configurations) < self._n_configs:
            self.logger.warning(f"Could only generate {len(configurations)} valid configurations out of {self._n_configs} requested.")
        return configurations
