# base/event.py

class Event:
    def __init__(self, pid, message):
        self.pid = pid
        self.message = message
        
    def apply(self, config, handler, handler_args=None, logger=None, animate=None):
        # apply this event (pid receives message) to the configuration
        # 'handler' is a parameter that contains protocol deciding logic
        
        process = config.processes[self.pid] # process object
        
        if not process.alive:
            if logger:
                logger.log_event({
                    "type": "skipped",
                    "pid": self.pid,
                    "reason": "process dead"
                })
            
            return False
        
        logger.log_event({
            "type": "receive",
            "pid": self.pid,
            "message": self.message
        })
            
        # delegate a handler
        round_advanced = handler(
            config, process, self.message,
            handler_args=handler_args,
            logger=logger,
            animate=animate)
        
        config.round += 1
        config.id = f"C{config.round}"
        return round_advanced