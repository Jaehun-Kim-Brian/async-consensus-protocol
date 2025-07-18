# base/process.py

import random

class Process:
    def __init__(self, pid, input_value, live=True):
        self.pid = pid
        self.x = input_value
        self.y = 'b' #undecided, blank
        self.alive = live
        self.state = {}
        self.pc = 0
        self.round = 0
        
    def __repr__(self):
        return (f"Process({self.pid}, x={self.x}, y={self.y}, "
                f"state={self.state}, round={self.round}, alive={self.alive}")
        
   