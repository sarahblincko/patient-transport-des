import simpy
import random
import pandas as pd

## Class for an Appointment Book
# read in the csv as pd dataframe
appt_book_pd = pd.read_csv("appt_book.csv")
#appt_book_pd.head()

## Class to store global parameters

class g:
    appt_book = appt_book_pd ## appointment book with collect_time and appt_time
    sim_duration = 1440  ## 24 hours in minutes
    number_of_runs = 1  ## 1 to start
    number_of_vehicles = 5 
    mean_transit_time = 15

## Class representing patients

class Patient:
        def __init__(self, p_id):
            self.id = p_id
            self.collect_time = 0 # from appt book
            self.appt_time = 0 # from appt book
            self.load_time = 0 # needed later
            self.transit_time = 0 # from appt book
            self.pt_arr_time = 0
            self.am_i_late = False


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
        self.results_df["Wait_Time"] = [0.0]
        self.results_df["Late"] = [0.0]
        self.results_df.set_index("Patient ID", inplace=True)
        
        # Create attributes to store the times in this run of the model
        self.mean_travel_time_time = 0

    # Generator Function for patient collection
    def generator_patients(self):
        for index, row in g.appt_book.iterrows():
            wait_time = row['collect_time'] - self.env.now 

            self.env.timeout(wait_time)
            no_patients=row['no_patients']
            for i in range(no_patients):
                # Increment patient counter
                self.patient_counter += 1
                # Create a new patient
                p = Patient(self.patient_counter)
                p.collect_time = row['collect_time'] # from appt book
                p.appt_time = row['appt_time'] # from appt book
                # #p.load_time = random.randint(1,15)
                # p.transit_time = g.appt_book.loc[g.appt_book['p_id'] == self.patient_counter, 'transit_time'] # from appt book
                p.transit_time = random.expovariate(1.0 / g.mean_transit_time)

            
                # Start the attend_appt generator
                self.env.process(self.attend_appt(p))

            
    # Generator Function for the pathway of the patient being transported to the appt
    def attend_appt(self, patient):
        start_wait_time = self.env.now 

        with self.vehicle.request() as req:
            # Freeze until vehicle available
            yield req

            end_wait_time = self.env.now

            patient.wait_time = end_wait_time - start_wait_time

          
        # pt_travel_time = g.appt_book.loc[g.appt_book['p_id'] == self.patient_counter, 'transit_time']
            
            yield self.env.timeout(patient.transit_time)

            patient.pt_arr_time = self.env.now

            if patient.pt_arr_time > patient.appt_time:
                patient.am_i_late==True

          # store results
            self.results_df.at[patient.id, "Wait_Time"] = (
                patient.wait_time)
            self.results_df.at[patient.id, "Late"] = (
                patient.am_i_late)
            

    def calculate_run_results(self):
        # Take the mean of the queuing times for the nurse across patients in
        # this run of the model.
        true_count = self.results_df[self.results_df.Late==True]
        self.num_late = len(true_count)

        self.mean_wait_time =self.results_df["Wait_Time"].mean()
    # The run method starts up the DES entity generators, runs the simulation,
    # and in turns calls anything we need to generate results for the run
    def run(self):
        # Start up our DES entity generators that create new patients.  We've
        # only got one in this model, but we'd need to do this for each one if
        # we had multiple generators.
        self.env.process(self.generator_patients())

        # Run the model for the duration specified in g class
        self.env.run(until=g.sim_duration)

        # Now the simulation run has finished, call the method that calculates
        # run results
        self.calculate_run_results()

        # Print the run number with the patient-level results from this run of 
        # the model
        print (f"Run Number {self.run_number}")
        print (self.results_df)


## Class for Trial of Simulation
class Trial:
    def __init__(self):
        self.df_trial_results = pd.DataFrame()
        self.df_trial_results["Run Number"] = [0]
        #self.df_trial_results["Mean Travel Time"] = [0.0]
        self.df_trial_results["Number of Late Patients"] = [0.0]
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
            self.df_trial_results.loc[run] = [my_model.num_late, 
                                              my_model.mean_wait_time]

        # Once the trial (ie all runs) has completed, print the final results
        self.print_trial_results()

# Create an instance of the Trial class
my_trial = Trial()

# Call the run_trial method of our Trial object
my_trial.run_trial()