import argparse
import matplotlib.pyplot as plt
from base_model import BaseInfectionModel
from states import State
from matplotlib.animation import FuncAnimation

STATE_COLORS = {
    State.SUSCEPTIBLE: "blue",
    State.EXPOSED: "orange",
    State.INFECTED: "red",
    State.RECOVERED: "green",
    State.DEAD: "black",
}

def plot_agents(model, ax):
    ax.clear()
    ax.set_xlim(0, model.grid.width)
    ax.set_ylim(0, model.grid.height)
    ax.set_title(f"Step: {model.schedule.time}")

    x_vals, y_vals, colors = [], [], []
    for agent in model.schedule.agents:
        if agent.pos is not None:
            x, y = agent.pos
            x_vals.append(x)
            y_vals.append(y)
            colors.append(STATE_COLORS[agent.state])

    ax.scatter(x_vals, y_vals, c=colors, alpha=0.8, edgecolors="k")
    dead_count = model.get_dead_count()
    if model.dead:
        ax.text(0, model.grid.height, f"Dead: {dead_count}", fontsize=12, color="red",
                bbox=dict(facecolor='white', alpha=0.8), verticalalignment="bottom", horizontalalignment="left")

def update(frame, model, ax_agents, ax_time, sus_line, inf_line, rec_line, exp_line, dead_line, 
            time_steps, sus_counts, inf_counts, rec_counts, exp_counts, ded_counts):
    model.step()
    plot_agents(model, ax_agents)

    time_steps.append(model.schedule.time)
    sus_counts.append(sum(1 for a in model.schedule.agents if a.state == State.SUSCEPTIBLE))
    inf_counts.append(sum(1 for a in model.schedule.agents if a.state == State.INFECTED))
    rec_counts.append(sum(1 for a in model.schedule.agents if a.state == State.RECOVERED))
    exp_counts.append(sum(1 for a in model.schedule.agents if a.state == State.EXPOSED) if model.exposed else 0)
    ded_counts.append(model.get_dead_count() if model.dead else 0)

    sus_line.set_data(time_steps, sus_counts)
    inf_line.set_data(time_steps, inf_counts)
    rec_line.set_data(time_steps, rec_counts)
    if model.exposed:
        exp_line.set_data(time_steps, exp_counts)
    if model.dead:
        dead_line.set_data(time_steps, ded_counts)

    return sus_line, inf_line, rec_line, exp_line, dead_line

def visualization(args):
    model = BaseInfectionModel(
        N=args.N,
        width=args.width,
        height=args.height,
        trans_p=args.trans_p,
        death_rate=args.death_rate,
        recover_days=args.recover_days,
        recover_std=args.recover_std,
        incubation_days=args.incubation_days,
        dead=args.dead,
        exposed=args.exposed
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    ax_agents, ax_time = axes

    ax_time.set_xlim(0, args.steps)
    ax_time.set_ylim(0, args.N)
    ax_time.set_xlabel("Steps")
    ax_time.set_ylabel("Agent Count")
    ax_time.set_title("Real-time Agent States")

    sus_line, = ax_time.plot([], [], label="Susceptible", color="#4381C1")
    exp_line, = ax_time.plot([], [], label="Exposed", color="#F49F0A") if model.exposed else (None,)
    inf_line, = ax_time.plot([], [], label="Infected", color='#F34213')
    rec_line, = ax_time.plot([], [], label="Recovered", color="#6BD425")
    dead_line, = ax_time.plot([], [], label="Deceased", color="#241623") if model.dead else (None,)

    ax_time.legend(loc="center right")
    ax_time.grid(True, linestyle='--', alpha=0.5)
    ax_time.set_facecolor("#F5F5F5")

    time_steps, sus_counts, inf_counts, rec_counts, exp_counts, dead_counts = [], [], [], [], [], []

    ani = FuncAnimation(fig, update, frames=args.steps, interval=200,
                         fargs=(model, ax_agents, ax_time, sus_line, inf_line, rec_line, exp_line, dead_line,
                                time_steps, sus_counts, inf_counts, rec_counts, exp_counts, dead_counts),
                         blit=False)

    ani.save('simulation.gif', writer='pillow', fps=5)
    plt.close()

def parse_args():
    parser = argparse.ArgumentParser(description="Run the infection model simulation.")
    parser.add_argument("--N", type=int, default=100, help="Number of agents")
    parser.add_argument("--width", type=int, default=10, help="Grid width")
    parser.add_argument("--height", type=int, default=10, help="Grid height")
    parser.add_argument('--exposed', action='store_true', help='Include Exposed')
    parser.add_argument('--dead', action='store_true', help='Include Deceased')
    parser.add_argument("--trans_p", type=float, default=0.2, help="Transmission probability")
    parser.add_argument("--death_rate", type=float, default=0.1, help="Death rate")
    parser.add_argument("--recover_days", type=int, default=21, help="Mean recovery days")
    parser.add_argument("--recover_std", type=int, default=7, help="Recovery time standard deviation")
    parser.add_argument("--incubation_days", type=int, default=5, help="Incubation period in days")
    parser.add_argument("--steps", type=int, default=100, help="Number of steps to run the model")
    return parser.parse_args()

def main():
    args = parse_args()
    visualization(args)

if __name__ == '__main__':
    main()
