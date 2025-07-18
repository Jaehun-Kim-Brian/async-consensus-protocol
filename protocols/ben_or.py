# protocols/ben_or.py

import random

def ben_or_handler(config, process, message, log=None, animate=None):
    #according to "Another Advantage of Free Choice: Completely Asynchronous Agreement Protocols"    
    n = len(config.processes)
    
    if 'vote' not in process.state:
        process.state['vote'] = process.x
    
    if 'seen' not in process.state:
        process.state['seen'] = set()
    
    if process.y in ['0', '1']:
        if log:
            log.append(f"{process.pid} has already decided y = {process.y}. No change.")
        return
    
    if message:
        sender, value = message
        process.state.setdefault('seen', set()).add((sender, value))
        if log:
            log.append(f"{process.pid} received vote={value} from {sender}")
    else:
        if log:
            log.append(f"{process.pid} received ⊥ (no message)")
            
    seen = process.state.get('seen', set())
    votes = [v for (_,v) in seen]
    
    if len(seen) >= n-1:
        # check majority
        if votes.count(0) > n//2:
            process.y = '0'
            process.state['vote'] = 0
            if log:
                log.append(f"{process.pid} DECIDES on 0")
        elif votes.count(1) > n//2:
            process.y = '1'
            process.state['vote'] = 1
            if log:
                log.append(f"{process.pid} DECIDES on 1")
        else:
            vote_random = random.choice([0, 1])
            process.state['vote'] = random.choice([0,1])
            if log:
                log.append(f"{process.pid} chooses randomly: vote = {vote_random}")
                
        process.round += 1
        process.state['seen'] = set()
        
    for target in config.processes:
        if target != process.pid:
            config.message_system.send(process.pid, target, process.state['vote'])
            if log:
                log.append(f"{process.pid} sends vote={process.state['vote']} to {target}")
        