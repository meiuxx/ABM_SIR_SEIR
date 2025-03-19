# Agent-Based Epidemic Modeling: SIR and SEIR Model Simulations

This project provides a stochastic Mesa implementation for simulating disease spread using SIR and SEIR compartmental models. The system emphasizes realistic agent interactions with configurable transmission dynamics, age-adjusted mortality risks, and progressive infection seeding to mirror real-world epidemic patterns. Simulation represents both spread over time and population dynamics. Below are example visualizations showing infection patterns in SIR (first) and SEIR with death tracking (second). Files may take time to load:

<img src="SIR.gif" width="550" alt="SIR Model"/> <img src="SEIRD.gif" width="550" alt="SEIR Model with death tracking"/>

## Overview

The modeling system consists of two primary components:

**`base_model.py`** contains the core functions. The BaseInfectionModel class manages the spatial environment through a Mesa MultiGrid. It also initializes population parameters and implements progressive infection seeding to avoid unrealistic initial case spikes.

**`agents.py`** defines the `Person` class representing individual agents. Each agent maintains health state transitions (SUSCEPTIBLE -> EXPOSED -> INFECTED -> RECOVERED/DEAD) and implements movement logic within the Moore neighborhood. Infection risk calculations use probabilistic compounding based on nearby infected neighbors (`1 - (1 - p)^n`) where `p` is the per-contact transmission probability, and `n` is the number of infected neighbors., while mortality risk scales with age through a linear adjustment factor for individuals over 50.

## Key Implementation Details

The model seeds infections gradually over 10 time steps. This prevents early spikes and creates more natural exponential growth curves. The seeding algorithm distributes infections across the warmup period while respecting the specified initial infection rate (default 1% of population).

Agents have age attribute assigned with normal distribution (μ=40, σ=10). Mortality risk increases linearly for agents over 50 through an age factor calculation: `min(1, max(0, (age - 50)/50))`. This scales the base death rate to create higher risk for older populations while maintaining valid probability bounds.

Infected agents determine recovery/death outcomes once at their recovery time threshold. Recovery durations follow a normal distribution with configurable mean and standard deviation. SEIR model introduces an exposed state where agents become infectious after an incubation period (normally distributed around specified mean).

## Command-Line Usage
To run model, run the file `run.py` which creates a visualization GIF, `simulation.gif`, inside the directory. Run with the command:

```bash
python run.py [ARGUMENTS]
```

### Key Arguments
`--N` Total number of agents in the simulation. Default: `100`

`--width` Width of the grid in cells. Default: `10`

`--height` Height of the grid in cells. Default: `10`

`--exposed` Enable the SEIR model (adds an "Exposed" state). Default: `False`

`--dead` Enable mortality tracking (adds a "Dead" state). Default: `False`

`--trans_p` Per-contact transmission probability. Default: `0.2`

`--death_rate`  Base mortality probability. Default: `0.1`

`--recover_days` Mean recovery duration in days. Default: `14`

`--recover_std` Standard deviation for recovery duration in days. Default: `7`

`--incubation_days` Mean incubation period for the SEIR model in days. Default: `5` 

`--steps` Number of simulation steps to run. Default: `100`

### Example Command
```bash
python run.py --N=500 --width=80 --height=80 --exposed --dead --trans_p=0.3 --steps=100
```


## Requirements
```bash
pip install mesa matplotlib numpy pillow
```
