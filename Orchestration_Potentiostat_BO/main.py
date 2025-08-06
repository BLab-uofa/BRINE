import nimsos
# import sys
import os
print(os.getcwd())
os.chdir("c:/Users/Blab2/Desktop/NIMSOS_base")

ObjectivesNum = 1
ProposalsNum = 1
CyclesNum = 121
Inputs = 5
Real_Inputs = Inputs # we do 1 for VERIFICATION (individual salt, no AI)

candidates_file = "./candidates.csv"
proposals_file = "./proposals.csv"


input_folder = "./EXPInput"
output_folder = "./EXPOutput"


#Create a list to store history
# res_history = nimsos.history(input_file = candidates_file,
#                              num_objectives = ObjectivesNum)

for K in range(CyclesNum):
    # Ki = K + 1
    print("Thou hast initiated process...", K+1)

    match K:
        case C if 0 <= C < 70:
            BO_type = "SMAC3"
        case C if 70 <= C < 100:
            BO_type = "SMAC3_EXPLOIT_REGION"
        case _:
             BO_type = "SMAC3_EXPLORE"
        
    nimsos.selection(method = BO_type,
                     input_file = candidates_file,
                     output_file = proposals_file,
                     num_objectives = ObjectivesNum,
                     num_proposals = ProposalsNum,
                     num_inputs = Inputs)
    


    #Creation of input files for robotic experiments and execution of robotic experiments.
    nimsos.preparation_input(machine = "STAN",
                             input_file = candidates_file,
                             input_folder = input_folder,
                             Real_Inputs = Real_Inputs,
                             Psycho = K+1)
    
    # nimsos.update_candidates(input_file = candidates_file,
    #                         proposals_file = proposals_file,
    #                         num_objectives = ObjectivesNum)

    #Analysis of results by robotic experiments and update of candidates files.
    nimsos.analysis_output(machine = "STAN",
                           input_file = candidates_file,
                           num_objectives = ObjectivesNum,
                           output_folder = output_folder,
                           Psycho = K+1)



    #Update list to store history
    # res_history = nimsos.history(input_file = candidates_file,
    #                              num_objectives = ObjectivesNum,
    #                              itt = K,
    #                              history_file = res_history)