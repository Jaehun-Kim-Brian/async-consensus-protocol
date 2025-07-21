# protocols/ben_or.py

import random

def majority_value(n, votes_list):
    if votes_list.count(0) > n//2:
        return 0
    elif votes_list.count(1) > n//2:
        return 1
    else:
        return None

def ben_or_handler(config, process, message, t=1, log=None, animate=None):
    #according to "Another Advantage of Free Choice: Completely Asynchronous Agreement Protocols"    
    n = len(config.processes)
    
    state = process.state
    state.setdefault('round', 1)
    state.setdefault('votes', [])
    state.setdefault('decisions', [])
    
    r= state['round']
    
    # already decided
    if process.y in ['0', '1']:
        if log:
            log.append(f"{process.pid} has already decided y = {process.y}. No change.")
        return
    
    # 1. receive message 
    if message:
        sender, msg_type, msg_round, msg_value = message
        
        if msg_round != r:
            if log:
                log.append(f"{process.pid} ignores message from {sender} (round message mismatch)")
            return
        
        if msg_type == 'vote':
            state['votes'].append(msg_value)
            if log:
                log.append(f"{process.pid} received vote={msg_value} from {sender} in round {r}")
                
        elif msg_type == 'decide':
            state['decisions'].append(msg_value)
            if log:
                log.append(f"{process.pid} received decision={msg_value} from {sender} in round {r}")
  
    # 2. decide value when votes are sufficient
    if len(state['votes']) >= n-t:
        majority = majority_value(n, state['votes'])
        if majority is not None:
            decision_msg = (process.pid, 'decide', r, majority)
        else:
            decision_msg = (process.pid, 'decide', r, '?')
                      
        for target in config.processes:
            if target != process.pid:
                config.message_system.send(
                    target, decision_msg
                )
                if log:
                    log.append(f"{process.pid} sends vote={process.state['votes']} to {target}")
        
        state['votes'].clear()
        
    # 3. if receive more than N - t 'decide' messages, 
    if len(state['decisions']) >= n - t:
        counts = {}
        for val in state['decisions']:
            if val != '?':
                counts[val] = counts.get(val, 0) + 1
            
        # There exists more than t D-messages with same value
        for v, cnt in counts.items():
            if cnt >= t + 1:
                process.y = v
                if log:
                    log.append(f"{process.pid} DECIDES {v} in round {r}")
                
                state['votes'].clear()
                state['decisions'].clear()
                state['round'] += 1
                break
        else:
            #There exists at leat one D-message    
            if counts: 
                chosen = next(iter(counts))
                process.x = chosen
                if log:
                    log.append(f"{process.pid} updates x ← {chosen} from D messages")
                
            else:
                rand_val = random.choice([0,1])
                process.x = rand_val
                if log:
                    log.append(f"{process.pid} randomly chooses x ← {rand_val}")
            
            state['votes'].clear()
            state['decisions'].clear()
            state['round'] += 1
    
    new_r = state['round']
    for target in config.processes:
        if target != process.pid:
            msg = (process.pid, 'vote', new_r, process.x)
            config.message_system.send(target, msg)
            if log:
                log.append(f"{process.pid} sends new vote={process.x} for round {new_r} to {target}.")