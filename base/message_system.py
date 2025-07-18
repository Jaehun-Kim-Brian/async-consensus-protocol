# base/message_system.py

import random
from collections import defaultdict

class MessageSystem:
    def __init__(self):
        self.buffer = defaultdict(list)
        
    def send(self, sender, receiver, message):
        #add messages to buffer in asynchronous way
        self.buffer[receiver].append((sender, message))
        
    def receive(self, receiver):
        #request to receive message indeterministically
        if receiver not in self.buffer or not self.buffer[receiver]:
            return None #buffer empty

        if random.random() < 0.7:
            return self.buffer[receiver].pop()
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
            for sender, msg in messages:
                summary.append(f"{sender} → {receiver}: {msg}")
        return summary or ["[Empty buffer]"]