from agents import Person
from mesa import  Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random
from states import State


class RandomScheduler:
    def __init__(self, model):
        self.model = model
        self.agents = []
        self.time = 0

    def add(self, agent):
        self.agents.append(agent)

    def step(self):
        random.shuffle(self.agents)
        for agent in self.agents:
            if agent.pos is not None and agent.state != State.DEAD:  # Skip agents without a position
                agent.step()
        self.time += 1

    def remove(self, agent):
        print(f"Removing agent {agent.unique_id} from the scheduler.")  # Debugging
        if agent in self.agents:
            self.agents.remove(agent)


class BaseInfectionModel(Model):
    def __init__(self, N=10, width=50, height=50, trans_p=0.2,
                 death_rate=0.1, recover_days=14, recover_std=7,
                 incubation_days=5, dead = False, exposed = False):
        super().__init__()
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.transmission_p = trans_p
        self.death_rate = death_rate
        self.recover_days = recover_days # mean mu
        self.recover_std = recover_std # standard deviation
        self.incubation_days = incubation_days
        self.schedule = RandomScheduler(self)
        self.dead = dead
        self.exposed = exposed
        self.running = True

        #we want to seed the initial infection to prevent sudden spikes of infections
        self.init_infected = int(self.num_agents*0.01)
        self.seed_duration = 10
        self.infections_seeded = 0

        
        # agent creation
        for _ in range(self.num_agents):
            a = Person(self)
            self.schedule.add(a)   
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y))

    
        self.datacollector = DataCollector(
            model_reporters = self.get_data_reporters()
        )
    
    def get_data_reporters(self):
        return {
                "Susceptible": lambda m: sum(1 for a in m.schedule.agents if a.state == State.SUSCEPTIBLE),
                "Exposed": (lambda m: sum(1 for a in m.schedule.agents if a.state == State.EXPOSED) if m.exposed else None),
                "Infected": lambda m: sum(1 for a in m.schedule.agents if a.state == State.INFECTED),
                "Recovered": lambda m: sum(1 for a in m.schedule.agents if a.state == State.RECOVERED or (not m.dead and a.state == State.DEAD)),
                "Dead": lambda m: sum(1 for a in m.schedule.agents if a.state == State.DEAD)
                }

    def seed_infection(self):
        if self.schedule.time < self.seed_duration:
            total_steps = self.seed_duration
            total_to_seed = self.init_infected
            base_per_step = total_to_seed // total_steps
            remainder = total_to_seed % total_steps

            if self.schedule.time < remainder:
                this_step = base_per_step + 1
            else:
                this_step = base_per_step

            susceptible = [agent for agent in self.schedule.agents if agent.state == State.SUSCEPTIBLE]
            possible_to_seed = min(this_step, len(susceptible), 
                                   self.init_infected - self.infections_seeded)

            if possible_to_seed > 0:
                chosen = self.random.sample(susceptible, possible_to_seed)
                for agent in chosen:
                    agent.state = State.INFECTED
                    agent.recovery_time = max(1, int(self.random.normalvariate(self.recover_days, self.recover_std)))
                    self.infections_seeded += 1


    def step(self):
        if (self.infections_seeded < self.init_infected):
            self.seed_infection()
        self.schedule.step() # update all agents
        self.datacollector.collect(self) # collect data

    def get_susceptible_count(self):
        return len([agent for agent in self.schedule.agents if agent.state == State.SUSCEPTIBLE])
    def get_infected_count(self):
        return len([agent for agent in self.schedule.agents if agent.state == State.INFECTED])
    def get_dead_count(self):
        return len([agent for agent in self.schedule.agents if agent.state == State.DEAD])
    