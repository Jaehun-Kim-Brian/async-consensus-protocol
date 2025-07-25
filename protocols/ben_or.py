# protocols/ben_or.py
from base.event import Event
import random

def majority_value(n, votes_list):
    if votes_list.count(0) > n//2:
        return 0
    elif votes_list.count(1) > n//2:
        return 1
    else:
        return None
            
def ben_or_handler(config, process, message, handler_args=None, t=1, logger=None, animate=None):
    #according to "Another Advantage of Free Choice: Completely Asynchronous Agreement Protocols"    
    n = handler_args.get('n', len(config.processes))
    t = handler_args.get('t', 1)
    state = process.state
    state.setdefault('round', 1)
    state.setdefault('votes', [])
    state.setdefault('decisions', [])
    state.setdefault('future', {})
    
    r= state['round']
    round_advanced = False
    
    # already decided
    if process.y in ['0', '1']:
        logger.log_event({
            "type": "already_decided",
            "pid": process.pid,
            "round": r,
            "value": process.y
        })
        return round_advanced
    
    # 1. receive message 
    if message:
        sender, msg_type, msg_round, msg_value = message
        if msg_round < r:
            logger.log_event({
                "type": "ignore_old_message",
                "pid": process.pid,
                "round": r,
                "message_round": msg_round,
                "from": sender
            })
            return round_advanced
        if msg_round > r:
            state['future'].setdefault(msg_round, []).append(message)
            logger.log_event({
                "type": "store_future_message",
                "pid": process.pid,
                "store_round": msg_round,
                "from": sender
            })
            return round_advanced
        if msg_type == 'vote':
            state['votes'].append(msg_value)
            logger.log_event({
                "type": "receive_vote",
                "pid": process.pid,
                "round": r,
                "from": sender,
                "value": msg_value
            })
        elif msg_type == 'decide':
            state['decisions'].append(msg_value)
            logger.log_event({
                "type": "receive_decision",
                "pid": process.pid,
                "round": r,
                "from": sender,
                "value": msg_value
            })
    
    else: # Receive no message : no change
        return round_advanced
    
    # 2. decide value when votes are sufficient
    if len(state['votes']) >= n-t:
        majority = majority_value(n, state['votes'])
        decision = majority if majority is not None else '?'
        decision_msg = (process.pid, 'decide', r, decision)
                      
        for target in config.processes:
            if target != process.pid:
                config.message_system.send(target, decision_msg)
                logger.log_event({
                    "type": "send_decision",
                    "from": process.pid,
                    "to": target,
                    "round": r,
                    "value": process.x
                })
        state['votes'].clear()
        return round_advanced
    
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
                logger.log_event({
                "type": "decide_final",
                "pid": process.pid,
                "round": r,
                "value": v
                })
                return round_advanced

        #There exists at least one D-message    
        if counts: 
            chosen = next(iter(counts))
            process.x = chosen
            logger.log_event({
                "type": "update_x_from_D",
                "pid": process.pid,
                "round": r,
                "new_x": chosen
            })
            
        else:
            rand_val = random.choice([0,1])
            process.x = rand_val
            logger.log_event({
                "type": "random_x_choice",
                "pid": process.pid,
                "round": r,
                "new_x": rand_val
            })
        
        state['decisions'].clear()
        state['round'] += 1
        round_advanced = True

        new_r = state['round']
        
        logger.log_event({
            "type": "advance_round",
            "pid": process.pid,
            "new_round": new_r
        })
            
        for target in  config.processes:
            if target != process.pid:
                msg = (process.pid, 'vote', new_r, process.x)
                config.message_system.send(target, msg)
                logger.log_event({
                    "type": "send_vote",
                    "from": process.pid,
                    "to": target,
                    "round": new_r,
                    "value": process.x
                })
    
        return round_advanced
    else:
        return round_advanced
    

def inject_future_messages(config, pid, logger=None):
    process = config.processes[pid]
    state = process.state
    current_r = state['round']
    
    if current_r in state.get('future', {}):
        messages = state['future'].pop(current_r)
        logger.log_event({
            "type": "inject_future_messages",
            "pid": pid,
            "round": current_r,
            "count": len(messages)
        })
        for msg in messages:
            event = Event(pid, msg)
            event.apply(config, handler=ben_or_handler, logger=logger)