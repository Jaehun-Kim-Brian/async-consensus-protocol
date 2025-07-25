# main.py

from base.process import Process
from base.message_system import MessageSystem
from base.configuration import Configuration
from base.event import Event
from protocols.ben_or import ben_or_handler, inject_future_messages
from utils.logger import SimulationLogger

import random

def simulate_ben_or(n=3, t=1, rounds=30, seed=None, log_enabled=True):
    if seed is not None:
        random.seed(seed)
        
    if not(0 <= t and n > 2*t):
        raise ValueError(f"Invalid parameters : Ben-Or requires n > 2t and t ≥ 0. Got n={n}, t={t}")
    handler_args = {'n': n, 't' : t}
        
    # 1. Generate processes & message system
    processes = [Process(f'P{i+1}', input_value=random.choice([0,1])) for i in range(n)]
    message_system = MessageSystem()
    config = Configuration(processes, message_system)
    
    # 2. log setting
    logger = SimulationLogger(enabled=log_enabled)
    
    # 3. Primary broadcast (input value based)
    for p in config.processes.values():
        for target in config.processes:
            if target != p.pid:
                message_system.send(target, (p.pid, 'vote', 1, p.x))
                logger.log_event({
                    "type": "send_initial_broadcast",
                    "from": p.pid,
                    "to": target,
                    "value": p.x
                })
                    
    # 4. Simulate event
    process_ids = list(config.processes.keys())
    for step in range(rounds):
        target = random.choice(process_ids)
        msg = message_system.receive(target)   
        
        logger.log_event({
            "type": "delivery_attemp",
            "receiver": target,
            "message": msg
        })
        
        event = Event(target, msg)
        round_advanced = event.apply(config, handler=ben_or_handler, handler_args=handler_args, logger=logger)
        
        if round_advanced:
            inject_future_messages(config, target, logger)
            
        logger.snapshot(config.get_state_summary())
            
        if config.all_decided():
            logger.final("All processes decided")
            break
        
    # 5. print log
    logger.export_as_json("simulation_log.json")
                
if __name__=="__main__":
    simulate_ben_or(rounds=300, log_enabled=True)