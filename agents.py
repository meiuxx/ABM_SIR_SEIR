from mesa import Agent
from states import State
import numpy as np


class Person(Agent):
    def __init__(self, model):
        Agent.__init__(self, model)
        self.dead = self.model.dead
        self.exposed = self.model.exposed
        self.age = max(5, self.random.normalvariate(40, 10)) 
        self.state = State.SUSCEPTIBLE
        self.infection_time = 0
        self.recovery_time = None
        self.incubation_time = None
        self.exposure_time = None
    
    def move(self):
        if self.pos is None or self.state == State.DEAD:
            return #dead cant move lol
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center = False)
        new_position = self.random.choice(possible_steps) # the choice of movement is random
        self.model.grid.move_agent(self, new_position)

    def contact(self):
        # FIXED: rather than letting infected agents try to infect, we let agent check if neighbors are infected
        if self.state == State.SUSCEPTIBLE:
            neighbour_agents = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True)
            infected_neighbors = sum(1 for n in neighbour_agents if n.state == State.INFECTED)
            
            if infected_neighbors > 0:
                prob = 1 - (1 - self.model.transmission_p) ** infected_neighbors
                if self.random.random() < prob:
                    if self.exposed:
                        self.state = State.EXPOSED
                        self.exposure_time = self.model.schedule.time
                        self.incubation_time = max(1, int(self.random.normalvariate(self.model.incubation_days, 2)))
                    else:
                        self.state = State.INFECTED
                        self.infection_time = self.model.schedule.time
                        self.recovery_time = max(1, int(self.random.normalvariate(self.model.recover_days, self.model.recover_std)))
    
    # check each agents' new infection status and work accordingly
    def status(self):
        if self.state == State.EXPOSED:
            # time spent in exposed state
            if (self.model.schedule.time - self.exposure_time) >= self.incubation_time:
                self.state = State.INFECTED
                self.recovery_time = max(1, int(self.random.normalvariate(self.model.recover_days, self.model.recover_std)))
            
        elif self.state == State.INFECTED and self.recovery_time is not None:
            age_factor = min(1, max(0, (self.age - 50) / 50))  # scaling for ages 50 to 100
            Adj_rate = min(1, max(0, self.model.death_rate * (1 + age_factor)))
            t = self.model.schedule.time - self.infection_time
            
            if t>=self.recovery_time:
                # determine survival once, at recovery time
                alive = np.random.choice([0,1], p=[Adj_rate, 1 - Adj_rate])
                if alive == 0:
                    if self.dead:
                        #remove from grid, KEEP IN SCHEDULER
                        self.model.grid.remove_agent(self)
                        self.state = State.DEAD
                    else:
                        # in SIR, dead count as recovered
                        self.state = State.RECOVERED
                else:
                    self.state = State.RECOVERED
    
    def step(self):
        self.status()
        self.contact()
        self.move()
