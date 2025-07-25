# utils/logger.py

from typing import List, Dict, Any
import json

class SimulationLogger:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.entries: List[Dict[str, Any]] = []
        self.step_counter = 0
        
    def log_event(self, event: Dict[str, Any]):
        if self.enabled:
            self.step_counter += 1
            entry = {
                "step": self.step_counter,
                **event
            }
            self.entries.append(entry)
            
    def snapshot(self, config_snapshot: Dict[str, Any]):
        if self.enabled:
            self.entries.append({
                "step": self.step_counter,
                "type": "snapshot",
                "state": config_snapshot
            })
            
    def final(self, message: str = None):
        if self.enabled:
            self.entries.append({
                "step": self.step_counter + 1,
                "type": "final",
                "message": message or "Simulation finished"
            })
            
    def export_as_dict(self) -> List[Dict[str, Any]]:
        return self.entries
    
    def export_as_json(self, path: str = "simulation_log.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)
            
    def print_log(self):
        if not self.enabled:
            print("Logging is disabled.")
            return
        for entry in self.entries:
            print(json.dumps(entry, indent=2, ensure_ascii=False))