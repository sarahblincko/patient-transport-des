import simpy
import random
import pandas as pd

## Class for an Appointment Book
# read in the csv as pd dataframe
appt_book_pd = pd.read_csv()

# p_id
# collect_time
# appt_time
# transit_time

## Class to store global parameters

class g:
    appt_book = appt_book_pd ## appointment book with collect_time and appt_time
    sim_duration = 1440  ## 24 hours in minutes
    number_of_runs = 1  ## 1 to start
    number_of_vehicles = 5 
    
setunim 
    
 


## Class representing patients

class Patient:
        def __init__(self, p_id):
            self.id = p_id
            self.collect_time = 0 # from appt book
            self.appt_time = 0 # from appt book
            self.load_time = 0 # this is needed later: random.randint(1,15)
            self.transit_time = 0 # from appt book




## Class for model of transport system
class Model:
    def __init__(self, run_number):
        self.env = simpy.Environment()
        ## Patient counter for patient ID
        self.patient_counter = 0


        # Resources
        self.vehicle = simpy.Resource(self.env, capacity = g.number_of_vehicles)

        # Store the passed in run number
        self.run_number = run_number
        # Pandas Dataframe for storing results
        self.results_df = pd.DataFrame()
        self.results_df["Patient ID"] = [1]
        self.results_df["Travel time"] = [0.0]
        self.results_df["Early/late"] = [0.0]
        self.results_df.set_index("Patient ID", inplace=True)
        
        # Create attributes to store the times in this run of the model
        self.mean_travel_time_time = 0

        # Generator Function for patient collection
        # This is an infinite loop, want to limit to number of patients in appt book
        while True:
            # Increment patient counter
            self.patient_counter += 1
            # Create a new patient
            p = Patient(self.patient_counter)
            
            # Start the attend_appt generator
            self.env.process(self.attend_appt(p))

            






## Class for Trial of Simulation
class Trial:
    def __init__(self):
        self.df_trial_results = pd.DataFrame()
        self.df_trial_results["Run Number"] = [0]
        self.df_trial_results["Mean Travel Time"] = [0.0]
        self.df_trial_results["Mean Number of Late Patients"] = [0.0]
        #self.df_trial_results[""] = [0.0] ##NEW
        self.df_trial_results.set_index("Run Number", inplace=True)

    # Method to print out the results from the trial.  In real world models,
    # you'd likely save them as well as (or instead of) printing them
    def print_trial_results(self):
        print ("Trial Results")
        print (self.df_trial_results)

    # Method to run a trial
    def run_trial(self):
        # Run the simulation for the number of runs specified in g class.
        # For each run, we create a new instance of the Model class and call its
        # run method, which sets everything else in motion.  Once the run has
        # completed, we grab out the stored run results (just mean queuing time
        # here) and store it against the run number in the trial results
        # dataframe.
        for run in range(g.number_of_runs):
            my_model = Model(run)
            my_model.run()
            
            ##NEW - added mean queue time for doctor to end of list
            self.df_trial_results.loc[run] = [my_model., # need once model class written
                                              my_model. # need once model class written
                                              ]

        # Once the trial (ie all runs) has completed, print the final results
        self.print_trial_results()

# Create an instance of the Trial class
my_trial = Trial()

# Call the run_trial method of our Trial object
my_trial.run_trial()