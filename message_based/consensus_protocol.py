import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from copy import deepcopy

'''
Process(pid, input_value)
    pid, x, y, pc, state, alive
    repr --> return internal state
    
MessageSystem
    buffer
    send(sender, receiver, message, log) --> append message to buffer[receiver], record log
    receive(receiver, log) --> receive first message in buffer[receiver]
'''
class Process:
    def __init__(self, pid, input_value):
        self.pid = pid
        self.x = input_value
        self.y = 'b'
        self.pc = 0 #program counter
        self.state = {}
        self.alive = True
        
    def __repr__(self):
        return f"Process({self.pid}, x={self.x}, y={self.y}, pc={self.pc}, state={self.state})"
    
class MessageSystem:
    def __init__(self):
        self.buffer = {}
        
    def send(self, sender, receiver, message, log):
        if receiver not in self.buffer:
            self.buffer[receiver] = []
        self.buffer[receiver].append((sender, message))
        if message is not None:
            log.append(f"{sender} → {receiver}: '{message}' [sent]")
        return f"{sender} → {receiver}: {message} [sent]"
    
    def receive(self, receiver, log):
        if receiver in self.buffer and self.buffer[receiver]:
            if random.random() < 0.7:
                msg = self.buffer[receiver].pop(0) # msg = (sender, message)
                sender = msg[0]
                message = msg[1]
                if msg is not None: #buffer[receiver] contains something,  but is it None?
                    log.append(f"{receiver} received '{message}' from {sender}")
                    return message
                else: 
                    log.append(f"{self.pid} received nothing (⊥). No state change.")
            else: #has something in buffer but cannot receive it
                log.append(f"{receiver} tried to receive: no delivery")
        else:
            if receiver not in self.buffer or not self.buffer[receiver]:
                log.append(f"{receiver} tried to receive: buffer empty")
        return None
            
    def snapshot(self):
        summary = []
        for receiver, messages in self.buffer.items():
            for sender, msg in messages:
                summary.append(f"  To {receiver}: '{msg}' from {sender}")
        if summary:
            return  "Message Buffer:\n" + "\n".join(summary)
        else:
            return "Message Buffer: empty"
    
class Configuration:
    def __init__(self, processes, message_system):
        self.step_counter = 0
        self.id = f"C0"
        self.processes = {p.pid: p for p in processes}
        self.message_system = message_system
        
    def decision_values(self):
        values = set()
        for p in self.processes.values():
            if p.y in ['0', '1']:
                values.add(p.y)
        return values
        
    def snapshot(self): 
        state_summary = [f"Configuration {self.id}, Process States:"]
        for pid, p in self.processes.items():
            state_summary.append(f"  {repr(p)}")
        buffer_summary = self.message_system.snapshot()
        return "\n".join(state_summary + [buffer_summary])#config : internal state of all processes + buffer
    
    def step_applied(self):
        self.step_counter += 1
        self.id = f"C{self.step_counter}"

class Event: # e = (p, m)
    def __init__(self, pid, message):
        self.pid = pid
        self.message = message #can be none
        
    def apply(self, config, log): 
        config.step_applied()
        process = config.processes[self.pid] #process object corresponding to pid
        if not process.alive: #no change
            log.append(f"{self.pid} is not alive. Event skipped.")
            return config 
        
        if self.message is not None:
            process.state['last_msg'] = self.message
            log.append(f"{self.pid} received '{self.message}' and updated state.")
            for target_pid in config.processes:
                if target_pid != self.pid:
                    sent_msg = f"echo:{self.message}"
                    config.message_system.send(self.pid, target_pid, sent_msg, log)
                    log.append(f"{self.pid} sent '{sent_msg}' to {target_pid}")
            if "0" in self.message:
                process.y = "0"
            elif "1" in self.message:
                process.y = "1"
                    
        else:
            log.append(f"{self.pid} received nothing (⊥). No state change.")
    
class Schedule:
    def __init__(self):
        self.events = []
        
    def generate_from_config(self, config, process_order, log):
        self.events.clear()
        log.append(f"\nGenerating schedule :")
        for pid in process_order: #according to process order, primarily conduct receive function
            msg = config.message_system.receive(pid, log)
            event = Event(pid, msg) #msg = None if pid didn't received
            self.events.append(event)
        log.append(f"---Schedule generated after conducting 'receive' {len(process_order)} times.---\n")
        
    def run(self, config, log): #message_based_protocol
        log.append(f"Initial {config.snapshot()}")
        
        for event in self.events:
            log.append(f"\nApplying event({event.pid}, {event.message})")
            event.apply(config, log)
            log.append(f"\nAfter event({event.pid}, {event.message})")
            log.append(f"{config.snapshot()}")
            log.append(f"Decision values: {config.decision_values()}")
        log.append("\nFinal Configuration:")
        log.append(config.snapshot())
        return "\n".join(log)

def message_based_basic_run(): 
    #initial configuration
    p1 = Process('P1', 0)
    p2 = Process('P2', 1)
    p3 = Process('P3', 1)
    
    message_system = MessageSystem()
    config = Configuration([p1, p2, p3], message_system)
    
    log = []
    
    #send primary message
    message_system.send('P1', 'P2', 'val=0', log)
    message_system.send('P1', 'P3', 'val=1', log)
    
    #generate schedule and run
    schedule = Schedule()
    schedule.generate_from_config(config, ['P2', 'P3', 'P2', 'P3'], log)
    log_output = schedule.run(config, log)
    return log_output

def simulate_message_based_run(process_order, initial_message):
    #initial configuration
    p1 = Process('P1', 0)
    p2 = Process('P2', 1)
    p3 = Process('P3', 1)
    message_system = MessageSystem()
    config = Configuration([p1, p2, p3], message_system)
    
    log = []
    #send primary message
    for sender, receiver, message in initial_message:
        message_system.send(sender, receiver, message, log)
        
    #generate schedule and run
    schedule = Schedule()
    schedule.generate_from_config(config, process_order, log)
    log_output = schedule.run(config, log)    
    
    return config.decision_values()
    message_system.send('P1', 'P2', 'val=0', log)
    
def bivalent_test_with_initial_messges():
    result_a = simulate_message_based_run(['P2', 'P3', 'P3'],[('P1', 'P2', 'val=0' )])
    result_b = simulate_message_based_run(['P3', 'P2', 'P2'],[('P1', 'P3', 'val=1' )])
    if(result_a == result_b):
        print(f"{result_a}-valent configuration")
    else:
        print("Bivalent configuration")
    
    
if __name__=="__main__":
    print(message_based_basic_run())
'''    
def run_simulation_1():
    p1 = Process('P1', 0)
    p2 = Process('P2', 1)
    p3 = Process('P3', 1)
    
    message_system = MessageSystem()
    config = Configuration([p1, p2, p3], message_system)
    
    log = []
    log.append(message_system.send('P1', 'P2', 'Hello P2'))
    log.append(message_system.send('P1', 'P3', 'Hello P3'))
    
    for _ in range(5):
        log.append(message_system.receive('P2'))
        log.append(message_system.receive('P3'))

    log.append("\nConfiguration Snapshot:")
    log.append(config.snapshot())

    return "\n".join(log)

def run_simulation_2():
    p1 = Process('P1', 0)
    p2 = Process('P2', 1)
    p3 = Process('P3', 1)
    
    message_system = MessageSystem()
    config = Configuration([p1, p2, p3], message_system)
    
    schedule = Schedule([
        Event('P2', 'Hello'),
        Event('P3', None),
        Event('P2', 'Hi again')
    ])
    
    final_config = schedule.run(config)
    return final_config.snapshot()
# 실행 결과 출력
print(run_simulation_2())
'''