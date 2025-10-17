from sokoban_state import State
from typing import List
import psutil, os

class SearchResult:
    """Container for search results."""
    
    def __init__(self, success: bool, solution: List[str] = None, 
                 states_explored: int = 0, time_taken: float = 0.0,
                 final_state: State = None, error_message: str = None,
                 memory_used_mb: float = 0.0, solver_name: str = "DFS"):
        self.success = success
        self.solution = solution or []
        self.states_explored = states_explored
        self.time_taken = time_taken
        self.final_state = final_state
        self.error_message = error_message
        self.memory_used_mb = memory_used_mb
        self.solver_name = solver_name
    
    def __str__(self):
        if self.success:
            return (
                f"Solver: {self.solver_name}\n"
                f"Solution found in {self.time_taken:.2f}s\n"
                f"States explored: {self.states_explored}\n"
                f"Memory used: {self.memory_used_mb:.2f} MB\n"
                f"Solution length: {len(self.solution)} moves\n"
                f"Solution: {''.join(self.solution)}"
            )
        else:
            return (
                f"Solver: {self.solver_name}\n"
                f"No solution found in {self.time_taken:.2f}s\n"
                f"States explored: {self.states_explored}\n"
                f"Memory used: {self.memory_used_mb:.2f} MB\n"
                f"Error: {self.error_message or 'Unknown'}"
            )

def get_memory_usage_mb() -> float:
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024