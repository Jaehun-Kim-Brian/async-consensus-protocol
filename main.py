# main.copy()

from base.process import Process
from base.message_system import MessageSystem
from base.configuration import Configuration
from base.event import Event

from protocols.ben_or import ben_or_handler

import random

def simulate_ben_or(n=3, rounds=30, seed=None, log_enabled=True):
    if seed is not None:
        random.seed(seed)
        
    # 1. Generate processes & message system
    processes = [Process(f'P{i+1}', input_value=random.choice([0,1])) for i in range(n)]
    message_system = MessageSystem()
    config = Configuration(processes, message_system)
    
    # 2. log setting
    log = [] if log_enabled else None
    
    # 3. Primary broadcast (input value based)
    for p in config.processes.values():
        for target in config.processes:
            if target != p.pid:
                message_system.send(target, (p.pid, 'vote', 1, p.x))
                if log is not None:
                    log.append(f"{p.pid} sends input {p.x} to {target}")
                    
    # 4. Simulate event
    process_ids = list(config.processes.keys())
    for step in range(rounds):
        target = random.choice(process_ids)
        msg = message_system.receive(target)
                
        event = Event(target, msg)
        event.apply(config, handler=ben_or_handler, log=log)
        
        if log is not None:
            log.append(f"[Step {step+1}] {config.snapshot()}")
            
        if len(config.decision_values()) == 1 and all(p.y in ['0', '1'] for p in config.processes.values()):
            if log is not None:
                log.append(f"All process decided on {list(config.decision_values())[0]}.")
            break
        
    # 5. print log
    if log is not None:
        print("\n".join(log))
    else: 
        print("Simulation finished (log disabled).")
                
if __name__=="__main__":
    simulate_ben_or(rounds=150, log_enabled=True)