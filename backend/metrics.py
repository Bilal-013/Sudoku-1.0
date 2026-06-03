""" Performance tracking class to measure steps, time, memory, etc. """
import time

class MetricsTracker:
    """ Tracks and aggregates AI algorithm performance metrics locally. """
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.time_elapsed = 0.0
        self.states_explored = 0
        self.backtracks = 0
        self.assignments_made = 0

    def start(self):
        self.start_time = time.time()
        self.end_time = None

    def stop(self):
        if self.start_time is not None:
            self.end_time = time.time()
            self.time_elapsed = self.end_time - self.start_time

    def record_backtrack(self):
        self.backtracks += 1

    def record_state(self):
        self.states_explored += 1

    def snapshot(self) -> dict:
        """ Returns the captured metrics as a standardized dictionary """
        current_elapsed = self.time_elapsed
        if self.start_time is not None and self.end_time is None:
            current_elapsed = time.time() - self.start_time
            
        return {
            "time_elapsed": current_elapsed,
            "states_explored": self.states_explored,
            "backtracks": self.backtracks,
            "assignments_made": self.assignments_made
        }
