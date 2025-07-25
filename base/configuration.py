# base/configuration.py

class Configuration:
    _config_counter = 0
    
    def __init__(self, processes, message_system):
        self.id = f"C{Configuration._config_counter}"
        Configuration._config_counter += 1
        
        self.processes = {p.pid: p for p in processes}
        self.message_system = message_system
        self.round = 0
        self.doen = 0 #number of processes that are in decision state
        
    def decision_values(self):
        return {p.y for p in self.processes.values() if p.y in [0, 1]}
    
    def snapshot(self):
        # document about current configuration summary
        lines = [f"[{self.id}] Configuration_Snapshot:"]
        for pid, proc in self.processes.items():
            lines.append(f"    {repr(proc)}")
        buffer_summary = self.message_system.snapshot()
        lines.append("Message Buffer:")
        lines.extend(f"    {line}" for line in buffer_summary)
        return "\n".join(lines)
    
    def get_state_summary(self):
        summary = {}
        for pid, p in self.processes.items():
            summary[pid] = {
                'x': p.x,
                'y': p.y,
                'alive': p.alive,
                'state': p.state.copy()
            }
        return summary
    
    def all_decided(self):
        return all(p.y in [0, 1] for p in self.processes.values())