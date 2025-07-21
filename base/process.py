# base/process.py

class Process:
    def __init__(self, pid, input_value, live=True):
        self.pid = pid
        self.x = input_value
        self.y = 'b' #undecided, blank
        self.alive = live
        self.state = {}
        self.pc = 0
        
    def __repr__(self):
        return (f"Process({self.pid}, x={self.x}, y={self.y}, "
                f"state={self.state}, alive={self.alive}")
