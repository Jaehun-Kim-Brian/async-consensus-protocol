# Re-execute necessary context after reset
import json
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
import numpy as np

# Load simulation log
with open("simulation_log.json", "r", encoding="utf-8") as f:
    simulation_log = json.load(f)

# Extract process IDs
process_ids = []
for entry in simulation_log:
    if entry['type'] == 'snapshot':
        process_ids = list(entry['state'].keys())
        break

n = len(process_ids)
angle_step = 2 * np.pi / n
node_positions = {
    pid: (np.cos(i * angle_step), np.sin(i * angle_step))
    for i, pid in enumerate(process_ids)
}

# Preprocess arrows per step
arrow_logs_by_step = {}
for entry in simulation_log:
    if entry['type'].startswith('send') and 'from' in entry and 'to' in entry:
        label = entry['type']
        if 'value' in entry:
            label += f" ({entry['value']})"
        arrow_logs_by_step.setdefault(entry['step'], []).append({
            'from': entry['from'],
            'to': entry['to'],
            'label': label
        })

# Collect frames
frames = []
for entry in simulation_log:
    if entry['type'] == 'snapshot':
        frames.append({
            'step': entry['step'],
            'title': f"Step {entry['step']}",
            'states': entry['state'],
            'arrows': arrow_logs_by_step.get(entry['step'], [])
        })

# Draw function
def draw_frame(frame_data, ax):
    ax.clear()
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.8, 1.8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(frame_data['title'], fontsize=16)

    for pid, (x, y) in node_positions.items():
        state = frame_data['states'][pid]
        color = 'lightgray' if state['y'] == 'b' else ('skyblue' if state['y'] == 0 else 'salmon')
        round_info = state.get('round', state['state'].get('round', '?'))
        ax.plot(x, y, 'o', markersize=30, color=color)
        text = f"{pid}\nx={state['x']}, y={state['y']}, r={round_info}"
        ax.text(x, y - 0.2, text, ha='center', fontsize=9)

    for arrow in frame_data.get('arrows', []):
        src = arrow['from']
        dst = arrow['to']
        label = arrow['label']
        if src in node_positions and dst in node_positions:
            sx, sy = node_positions[src]
            dx, dy = node_positions[dst]
            ax.annotate(
                '', xy=(dx, dy), xytext=(sx, sy),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5)
            )
            mid_x = (sx + dx) / 2
            mid_y = (sy + dy) / 2
            ax.text(mid_x, mid_y, label, fontsize=8, ha='center', va='center')

# Animate
fig, ax = plt.subplots(figsize=(6, 6))
ani = FuncAnimation(fig, lambda i: draw_frame(frames[i], ax), frames=len(frames), interval=1000, repeat=False)

# Save
gif_path = "ben_or_simulation.gif"
mp4_path = "ben_or_simulation.mp4"

ani.save(gif_path, writer=PillowWriter(fps=1))
ani.save(mp4_path, writer=FFMpegWriter(fps=1))

gif_path, mp4_path
