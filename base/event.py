# base/event.py

class Event:
    def __init__(self, pid, message):
        self.pid = pid
        self.message = message
        
    def apply(self, config, handler, log=None, animate=None):
        # apply this event (pid receives message) to the configuration
        # 'handler' is a parameter that contains protocol deciding logic
        
        process = config.processes[self.pid] # process object
        
        if not process.alive:
            if log:
                log.append(f"{self.pid} is not alive. Event skipped.")
            return
        
        if log:
            log.append(f"Event: {self.pid} receives {self.message}")
            
        # delegate a handler
        handler(config, process, self.message, log=log, animate=animate)
        
        config.round += 1
        config.id = f"C{config.round}"