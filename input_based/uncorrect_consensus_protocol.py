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
class ProcessInputBased:
    def __init__(self, pid, input_value):
        self.pid = pid
        self.x = input_value
        self.y = 'b'
        self.pc = 0 #program counter
        self.state = {}
        self.alive = True
        
    def __repr__(self):
        return f"Process({self.pid}, x={self.x}, y={self.y}, state={self.state})"
    
class MessageSystem:
    def __init__(self):
        self.buffer = {}
        
    def send(self, sender, receiver, message, log):
        if receiver not in self.buffer:
            self.buffer[receiver] = []
        self.buffer[receiver].append((sender, message))
        if message is not None:
            log.append(f"{sender} → {receiver}: '{message}' [sent]")
        #return f"{sender} → {receiver}: {message} [sent]"
    
    def receive(self, receiver, log):
        if receiver in self.buffer and self.buffer[receiver]:
            sender, msg = self.buffer[receiver][0]
            if random.random() < 0.7:
                self.buffer[receiver].pop(0)
                if msg is not None: #buffer[receiver] contains something,  but is it None?
                    log.append(f"{receiver} received '{msg}' from {sender}")
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
            for sender, msg in messages:
                summary.append(f"  To {receiver}: '{msg}' from {sender}")
        if summary:
            return  "Message Buffer:\n" + "\n".join(summary)
        else:
            return "Message Buffer: empty"
    
class ConfigInput:
    def __init__(self, processes, message_system):
        self.step_counter = 0
        self.id = f"C0"
        self.processes = {p.pid: p for p in processes}
        self.message_system = message_system
        
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
        self.message = message #can be none
        
    def apply(self, config, log): 
        config.step_applied()
        process = config.processes[self.pid] #process object corresponding to pid
        if not process.alive: #no change
            log.append(f"{self.pid} is not alive. Event skipped.")
            return config 
        
        if self.message is not None:
            process.state['last_msg'] = self.message
            
            if "0" in self.message:
                process.y = "0"
            elif "1" in self.message:
                process.y = "1"
            log.append(f"{self.pid} received '{self.message}' → y = {process.y}")
            
            for target_pid in config.processes: #broadcast
                if target_pid != self.pid:
                    config.message_system.send(self.pid, target_pid, f"echo: val={process.y}", log)       
        else:
            log.append(f"{self.pid} received nothing (⊥). No state change.")
    
class ScheduleInputBased:
    def __init__(self):
        self.events = []
        
    def generate_from_config(self, config, process_order, log):
        self.events.clear()
        log.append(f"\nGenerating schedule :")
        for pid in process_order: #according to process order, primarily conduct receive function
            msg = config.message_system.receive(pid, log)
            event = EventInputBased(pid, msg) #msg = None if pid didn't received
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
        log.append("\n---Final Configuration---")
        log.append(config.snapshot())
        log.append(f"Decision values: {config.decision_values()}")
        return "\n".join(log)


def simulate_input_based_run(process_order, input_values):
    #initial configuration
    processes = [ProcessInputBased(pid, x) for pid, x in input_values]
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
    schedule.generate_from_config(config, process_order, log)
    log_output = schedule.run(config, log)    
    
    return log_output
    
def bivalent_test_with_initial_messges():
    print(simulate_input_based_run(['P2', 'P3', 'P3'],[('P1', 'P2', 'val=0' )]))
    print(simulate_input_based_run(['P3', 'P2', 'P2'],[('P1', 'P3', 'val=1' )]))
    
#def simulate_input_based_run():
    pass

def bivalent_test_with_input_config():
    pass

    
    
if __name__=="__main__":
    log_result = simulate_input_based_run(
        process_order=['P2', 'P3', 'P2'],
        input_values=[('P1', 0), ('P2', 1), ('P3', 1)]
    )
    print(log_result)
    