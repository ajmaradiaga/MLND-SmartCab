import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import sys, getopt
from collections import OrderedDict 

args_dict = OrderedDict()
args_dict["learning"] = False
args_dict["alpha"] = 0.5
args_dict["epsilon"] = 1.0
args_dict["enforce_deadline"] = False
args_dict["update_delay"] = 0.01
args_dict["display"] = False 
args_dict["log_metrics"] = True 
args_dict["optimized"] = False
args_dict["n_test"] = 10 
args_dict["tolerance"]= 0.05
args_dict["decay_fx"]= "None"
args_dict["params_output"]= ""

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed
        self.trial_num = 0.0
        
        random.seed(888) 


    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0
        
        if testing:
            self.epsilon = 0.0
            self.alpha = 0.0
        else:
            #bad actions, major violation, major accident, rolling avg reward per action, reliability
            self.trial_num += 1.0
            
            if args_dict["decay_fx"] == "initial":
                self.epsilon = self.epsilon - 0.05
            elif args_dict["decay_fx"] == "oneovertp2":
                self.epsilon = 1 / (self.trial_num ** 2)
            elif args_dict["decay_fx"] == "expat":
                self.epsilon = math.exp(-self.alpha * self.trial_num)
            elif args_dict["decay_fx"] == "cosat":
                self.epsilon = math.cos(self.alpha * self.trial_num)
            else:
                self.epsilon = 0.0
            #self.epsilon = 1 / (self.trial_num ** 2)
            
            #0.001, 0.001, 0.001, 1.5, 80 peak 90
            #alpha=0.01, epsilon=1.0, tolerance=0.01
            
            #0.035, 0.0212, 0.01, 0.9, 40 peak 90
            #alpha=0.05, epsilon=1.0, tolerance=0.01
            
            
            #0.1711, 0.1283, 0.0428, -1.8, 40 peak 40
            #alpha=0.05, epsilon=1.0, tolerance=0.01
            #
        

        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint 
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        # Set 'state' as a tuple of relevant data for the agent
        state = (inputs["light"], inputs["oncoming"], inputs["left"], inputs["right"], waypoint)

        return state


    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ########### 
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state
        maxQ = -8888.8
        q_state = self.Q[state]
        
        for action, value in q_state.iteritems():
            if maxQ < value:
                maxQ = value

        return maxQ 


    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0
        if self.learning == True and state not in self.Q:
            self.Q[state] = {action : 0.0 for action in self.valid_actions }
            
        return


    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        
        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        # When learning, choose a random action with 'epsilon' probability
        #   Otherwise, choose an action with the highest Q-value for the current state
        
        if self.learning == True:
            if random.random() < self.epsilon:
                action = random.choice(self.valid_actions)
            else:
                maxQ = self.get_maxQ(state)
                action = random.choice([k for k,v in self.Q[state].iteritems() if v == maxQ])
                            
        else:
            action = random.choice(self.valid_actions)
 
        return action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
        if self.learning == True:
            self.Q[state][action] += (self.alpha * reward)

        return


    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return

def run(argv):
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    args_dict = parse_commands(argv)
    
    if len(args_dict["params_output"]) > 0:
        f = open(args_dict["params_output"], 'wb')
        for k,v in args_dict.iteritems():
            f.write("{} = {} {}\n".format(k, v, type(v)))
        f.close() 
    
    
    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment()
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent, \
                             learning=args_dict["learning"], \
                             alpha=args_dict["alpha"], \
                             epsilon=args_dict["epsilon"])
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=args_dict["enforce_deadline"])

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, \
                    update_delay=args_dict["update_delay"], \
                    log_metrics=args_dict["log_metrics"], \
                    optimized=args_dict["optimized"], \
                    display=args_dict["display"])
    
    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(n_test=args_dict["n_test"], \
            tolerance=args_dict["tolerance"])

def parse_commands(argv):
    
    
    help_string = ""
    default_string = "\n\nDefault values:\n"
    for k, v in args_dict.iteritems():
        help_string += "--" + k + " " + str(type(v)) + " "
        default_string += "--"+k + " " + str(v) + " \n"
    
    help_string += default_string
    
    try:
        if len(argv) == 0:
            print("No parameters defined.")
            return args_dict
        opts, args = getopt.getopt(argv,"hl:a:e:ud:d:lm:op:nt:tol",["help"] + [k + "=" for k in args_dict])
    except getopt.GetoptError:
        print 'agent.py ' + help_string
        sys.exit(2)
    for opt, arg in opts:
        opt = opt.replace("--", "")
        # print(opt, arg)
        if opt in ("-h", '--help'):
            print 'agent.py ' + help_string
            sys.exit()
        elif type(args_dict[opt]) == bool:
            args_dict[opt] = True if arg.lower() in ("yes", "true", "t", "1") else False
        elif opt in args_dict:
            args_dict[opt] = type(args_dict[opt])(arg)
        
    return args_dict

if __name__ == '__main__':
    run(sys.argv[1:])