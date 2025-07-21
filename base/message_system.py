# base/message_system.py

import random
from collections import defaultdict

class MessageSystem:
    def __init__(self):
        self.buffer = defaultdict(list)
        
    def send(self, receiver, message):
        #add messages to buffer in asynchronous way
        self.buffer[receiver].append(message)
        
    def receive(self, receiver):
        #request to receive message indeterministically
        if receiver not in self.buffer or not self.buffer[receiver]:
            return None #buffer empty

        if random.random() < 0.7:
            return self.buffer[receiver].pop(0)
        else:
            return None
        
    def peek_buffer(self, receiver=None):
        if receiver:
            return self.buffer.get(receiver, [])
        return dict(self.buffer)
    
    def all_receivers(self):
        return list(self.buffer.keys())
    
    def snapshot(self):
        summary = []
        for receiver, messages in self.buffer.items():
            for msg in messages: #msg : (sender, msg_type, msg_round, msg_value)
                summary.append(f"{msg[0]} → {receiver}: {msg[1:]}")
        return summary or ["[Empty buffer]"]