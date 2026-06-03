""" Performance tracking class to measure steps, time, memory, etc. """
import time

class MetricsTracker:
    """ Tracks and aggregates AI algorithm performance metrics locally. """
    
    def __init__(self):
        self.start_time = time.time()
        self.nodes_expanded = 0
        self.steps_taken = 0

    def get_metrics_dict(self) -> dict:
        """ Returns the captured metrics as a standardized dictionary """
        return {
            "time_taken_ms": (time.time() - self.start_time) * 1000,
            "nodes_expanded": self.nodes_expanded,
            "steps_taken": self.steps_taken
        }
