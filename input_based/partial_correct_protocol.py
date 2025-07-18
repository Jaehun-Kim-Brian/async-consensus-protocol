import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import matplotlib.animation as animation
import random

class ProcessInputBased:
    def __init__(self, pid, input_value, live=True):
        self.pid = pid
        self.x = input_value
        self.y = 'b'
        self.pc = 0 #program counter
        self.state = {'sender':[], 'sum' : 0}
        self.alive = live
        
    def __repr__(self):
        return f"Process({self.pid}, x={self.x}, y={self.y}, state=[sender : {self.state['sender']}, sum : {self.state['sum']}])"
    
class MessageSystem:
    def __init__(self):
        self.buffer = {}
        
    def send(self, sender, receiver, message, log):
        if receiver not in self.buffer:
            self.buffer[receiver] = []
        self.buffer[receiver].append((sender, message))
        if message is not None:
            log.append(f"{sender} → {receiver}: '{message}' [sent]")
        
    def receive(self, receiver, log):
        if receiver in self.buffer and self.buffer[receiver]:
            msg = self.buffer[receiver][0] #msg = (sender, message)
            if random.random() < 0.7:
                self.buffer[receiver].pop(0)
                if msg[1] is not None: #buffer[receiver] contains something,  but is it None?
                    log.append(f"{receiver} received '{msg[1]}' from {msg[0]}")
                    return msg
                else: 
                    log.append(f"{self.pid} received nothing (⊥). No state change.")
            else: #has something in buffer but cannot receive it
                log.append(f"{receiver} tried to receive: no delivery")
        else:
            log.append(f"{receiver} tried to receive: buffer empty")
        return None
            
    def snapshot(self):
        summary = []
        for receiver, messages in self.buffer.items():
            for sender, message in messages:
                summary.append(f"From {sender} to {receiver}: '{message}'")
        if summary:
            return  "Message Buffer:\n" + "\n".join(summary)
        else:
            return "Message Buffer: empty"
    
class ConfigInput:
    def __init__(self, processes, message_system):
        self.step_counter = 0
        self.id = f"C0"
        self.processes = {p.pid: p for p in processes}
        self.process_num = len(processes)
        self.message_system = message_system
        self.done = 0
        
    def decision_values(self):
        return {p.y for p in self.processes.values() if p.y in ['0', '1']}
        
    def snapshot(self): 
        state_summary = [f"Configuration {self.id}, Process States:"]
        for pid, p in self.processes.items():
            state_summary.append(f"  {repr(p)}")
        buffer_summary = self.message_system.snapshot()
        return "\n".join(state_summary + [buffer_summary])#config : internal state of all processes + buffer
    
    def step_applied(self):
        self.step_counter += 1
        self.id = f"C{self.step_counter}"

class EventInputBased: # e = (p, m)
    def __init__(self, pid, message):
        self.pid = pid
        self.msg = message #can be none
        
    def apply(self, config, log): 
        config.step_applied()
        process = config.processes[self.pid] #process object corresponding to pid
        if not process.alive: #no change
            log.append(f"{self.pid} is not alive. Event skipped.")
            return config 
        
        if process.y in ['0', '1']: #already decided
            log.append(f"{self.pid} has already decided y = {process.y}, no change.")
            
        if self.msg is not None:
            message_sender = self.msg[0]
            message = self.msg[1]
            if message_sender not in process.state['sender']:
                log.append(f"{self.pid} received '{message}' from {message_sender}")
                process.state['sender'].append(message_sender)
                if "1" in message:
                    process.state['sum'] += 1
                if len(process.state['sender']) >= config.process_num -1:
                    config.done += 1
                    deciding_value = process.state['sum'] + config.processes[self.pid].x
                    if deciding_value > (config.process_num // 2):
                        process.y = '1'
                        log.append(f"{self.pid} decided to '1'.")
                    else:
                        process.y = '0'
                        log.append(f"{self.pid} decided to '0'.")
                    
            
                for target_pid in config.processes: #broadcast
                    if target_pid != self.pid:
                        config.message_system.send(self.pid, target_pid, f"echo: {self.msg[1]}", log)
            else:
                log.append(f"{self.pid} already received from {message_sender}. No state change.")      
        else:
            log.append(f"{self.pid} received nothing (⊥). No state change.")
    
class ScheduleInputBased:
    def __init__(self):
        self.process_order = []
        
    def generate_process_order(self, process_sequence, log):
        self.process_order = process_sequence 
        
        log.append(f"\nGenerating Process Order :")
        log.append(f"{' '.join(pid for pid in self.process_order[:20])} ...")
        log.append(f"---Schedule consists of {len(process_sequence)} events generated by receiving messages in process order!\n")
        
    def run(self, config, log): #message_based_protocol
        log.append(f"Initial {config.snapshot()}")
        
        for pid in self.process_order:
            if config.done >= config.process_num:
                break
            msg = config.message_system.receive(pid, log)
            event = EventInputBased(pid, msg)
            log.append(f"\nApplying event({pid}, {event.msg})")
            event.apply(config, log)
            log.append(f"\nAfter event({pid}, {event.msg})")
            log.append(f"{config.snapshot()}")
            log.append(f"Decision values: {config.decision_values()}")
        log.append("\n---Final Configuration---")
        log.append(config.snapshot())
        log.append(f"Decision values: {config.decision_values()}")
        return "\n".join(log)

def simulate_run(input_values, process_sequence):
    #initial configuration
    processes = []
    for input_value in input_values:
        if len(input_value) == 3:
            processes.append(ProcessInputBased(input_value[0], input_value[1], input_value[2]))
        else:
            processes.append(ProcessInputBased(input_value[0], input_value[1]))

    message_system = MessageSystem()
    config = ConfigInput(processes, message_system)
    
    log = []
    #send primary message
    for p in config.processes.values():
        for target in config.processes:
            if target != p.pid:
                message_system.send(p.pid, target, f"val={p.x}", log)
    
    #generate schedule and run
    schedule = ScheduleInputBased()
    schedule.generate_process_order(process_sequence, log)
    log_output = schedule.run(config, log)    
    
    return log_output

def show_partial_correct_protocol(schedule_limit):
    candidates = ['P1', 'P2', 'P3']
    process_sequence = [candidates[random.randint(0, 1000000) % 3] for _ in range(schedule_limit)]
    log_result = simulate_run(
        input_values=[('P1', 0), ('P2', 1), ('P3', 1)], 
        process_sequence=process_sequence
    )
    return log_result

def show_contradiction_for_LEMMA2(schedule_limit):
    candidates = ['P1', 'P2', 'P3']
    process_sequence = [candidates[random.randint(0, 1000000) % 3] for _ in range(schedule_limit)]
    
    log_result_a = simulate_run(
        input_values=[('P1', 0), ('P2', 1), ('P3', 1, False)], 
        process_sequence=process_sequence
    )
    
    log_result_b = simulate_run(
        input_values=[('P1', 0), ('P2', 1), ('P3', 0, False)], 
        process_sequence=process_sequence
    )
    print(log_result_a[-5:], log_result_b[-5:])

node_positions = {
    'P1': (0.5, 1.0),
    'P2': (0.0, 0.0),
    'P3': (1.0, 0.0)
}

colors = {
    'P1': 'skyblue',
    'P2': 'lightgreen',
    'P3': 'salmon'
}

frames = [
    {
        'title': 'Initial Broadcast',
        'messages': [('P1', 'P2'), ('P1', 'P3'), ('P2', 'P1'), ('P2', 'P3'), ('P3', 'P1'), ('P3', 'P2')],
        'states': {
            'P1': {'x': 0, 'y': 'b', 'sum': 0, 'sender': [], 'alive': True},
            'P2': {'x': 1, 'y': 'b', 'sum': 0, 'sender': [], 'alive': True},
            'P3': {'x': 1, 'y': 'b', 'sum': 0, 'sender': [], 'alive': True}
        }
    },
    {
        'title': 'P2 Receives from P1',
        'messages': [('P1', 'P2')],
        'states': {
            'P1': {'x': 0, 'y': 'b', 'sum': 0, 'sender': [], 'alive': True},
            'P2': {'x': 1, 'y': 'b', 'sum': 0, 'sender': ['P1'], 'alive': True},
            'P3': {'x': 1, 'y': 'b', 'sum': 0, 'sender': [], 'alive': True}
        }
    },
    {
        'title': 'P2 Broadcasts',
        'messages': [('P2', 'P1'), ('P2', 'P3')],
        'states': {
            'P1': {'x': 0, 'y': 'b', 'sum': 0, 'sender': [], 'alive': True},
            'P2': {'x': 1, 'y': '0', 'sum': 1, 'sender': ['P1'], 'alive': True},
            'P3': {'x': 1, 'y': 'b', 'sum': 0, 'sender': [], 'alive': True}
        }
    }
]


def draw_frame(frame_data, ax):
    ax.clear()
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.2, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.set_title(frame_data['title'], fontsize=16)
    
    #Node and its status
    for pid, (x,y) in node_positions.items():
        ax.plot(x, y, 'o', markersize=30, color=colors[pid])
        state = frame_data['states'][pid]
        text = f"{pid}\nx={state['x']}, y={state['y']}\nsum={state['sum']}\nsenders={state['sender']}"
        ax.text(x, y - 0.12, text, ha='center', fontsize=9)
    
    #Message arrow
    for sender, receiver in frame_data['messages']:
        sx, sy = node_positions[sender]
        rx, ry = node_positions[receiver]
        dx, dy = rx - sx, ry - sy
        dist = (dx**2 + dy**2) ** 0.5
        offset = 0.08
        start = (sx + offset * dx / dist, sy + offset * dy / dist)
        end = (rx - offset * dx / dist, ry - offset * dy / dist)
        arrow = FancyArrowPatch(start, end, arrowstyle='->', mutation_scale=15, color='gray')
        ax.add_patch(arrow)
        
def animate_visualization(frames):
    fig, ax = plt.subplots(figsize=(6, 6))
    def update(i):
        draw_frame(frames[i], ax)
    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=1500, repeat=False)
    ani.save("flp_simulation.gif", writer='pillow', fps=1)

# 시각화 실행

if __name__=="__main__":
    schedule_limit = 30
    #print(show_partial_correct_protocol(schedule_limit))
    #show_contradiction_for_LEMMA2(schedule_limit)
    animate_visualization(frames)
    