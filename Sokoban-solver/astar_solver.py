"""
A* Search Algorithm for Sokoban.
"""

import heapq
import time
import psutil
import os
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict

from sokoban_state import AStarState
from move_generation import MoveGenerator
from heuristics import get_heuristic_function
from deadlock_detection import detect_deadlock

class SearchResult:
    """Container for search results."""
    
    def __init__(self, success: bool, solution: List[str] = None, 
                 states_explored: int = 0, time_taken: float = 0.0,
                 final_state: AStarState = None, error_message: str = None,
                 memory_used_mb: float = 0.0):
        self.success = success
        self.solution = solution or []
        self.states_explored = states_explored
        self.time_taken = time_taken
        self.final_state = final_state
        self.error_message = error_message
        self.memory_used_mb = memory_used_mb
    
    def __str__(self):
        if self.success:
            return (f"Solution found in {self.time_taken:.2f}s\n"
                   f"States explored: {self.states_explored}\n"
                   f"Memory used: {self.memory_used_mb:.2f} MB\n"
                   f"Solution length: {len(self.solution)} moves\n"
                   f"Solution: {''.join(self.solution)}")
        else:
            return (f"No solution found in {self.time_taken:.2f}s\n"
                   f"States explored: {self.states_explored}\n"
                   f"Memory used: {self.memory_used_mb:.2f} MB\n"
                   f"Error: {self.error_message or 'Unknown'}")

def get_memory_usage_mb() -> float:
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

class AStarSolver:
    """A* search algorithm implementation for solving Sokoban."""
    
    def __init__(self, max_states: int = 100000, max_time: float = 300.0, use_deadlock_detection: bool = True):
        """
        Initialize A* solver with configuration.
        
        Args:
            max_states: Maximum states to explore before giving up.
            max_time: Maximum time in seconds before timeout.
            use_deadlock_detection: Whether to use deadlock pruning.
        """
        self.heuristic_func = get_heuristic_function()
        self.max_states = max_states
        self.max_time = max_time
        self.use_deadlock_detection = use_deadlock_detection
        
        # Search statistics
        self.states_explored = 0
        self.states_generated = 0
        self.deadlocks_detected = 0
        self.duplicate_states = 0
        
    def solve(self, initial_state: AStarState) -> SearchResult:
        """
        Solve the Sokoban puzzle using A* search.
        
        Args:
            initial_state: Starting state of the puzzle.
            
        Returns:
            SearchResult containing solution and statistics.
        """
        start_time = time.time()
        initial_memory = get_memory_usage_mb()
        
        # Reset statistics.
        self.states_explored = 0
        self.states_generated = 0
        self.deadlocks_detected = 0
        self.duplicate_states = 0
        
        # Check if initial state is already solved.
        if initial_state.is_goal_state():
            final_memory = get_memory_usage_mb()
            return SearchResult(
                success=True, 
                solution=[], 
                states_explored=1,
                time_taken=time.time() - start_time,
                final_state=initial_state,
                memory_used_mb=final_memory - initial_memory,
            )
        
        # Initialize search data structures.
        open_list = []  # Priority queue (heap).
        closed_set = set()  # Set of explored state keys.
        state_costs = {}  # Best known g-costs for states.
        
        # Calculate initial heuristic.
        initial_state.h_cost = self.heuristic_func(initial_state)
        initial_state.g_cost = 0
        initial_state.f_cost = initial_state.g_cost + initial_state.h_cost
        
        heapq.heappush(open_list, (initial_state.f_cost, 0, initial_state))
        state_costs[initial_state.get_state_key()] = 0
        
        # Main search loop.
        while open_list:
            # Check timeout.
            if time.time() - start_time > self.max_time:
                final_memory = get_memory_usage_mb()
                return SearchResult(
                    success=False,
                    states_explored=self.states_explored,
                    time_taken=time.time() - start_time,
                    error_message=f"Timeout after {self.max_time}s",
                    memory_used_mb=final_memory - initial_memory,
                )
            
            # Check state limit.
            if self.states_explored >= self.max_states:
                final_memory = get_memory_usage_mb()
                return SearchResult(
                    success=False,
                    states_explored=self.states_explored,
                    time_taken=time.time() - start_time,
                    error_message=f"State limit reached ({self.max_states})",
                    memory_used_mb=final_memory - initial_memory,
                )
            
            # Get next state from priority queue.
            f_cost, tiebreaker, current_state = heapq.heappop(open_list)
            
            # Skip if we've already explored a better path to this state.
            state_key = current_state.get_state_key()
            if state_key in closed_set:
                continue
            
            # Mark state as explored.
            closed_set.add(state_key)
            self.states_explored += 1
            
            # Check if goal reached.
            if current_state.is_goal_state():
                solution_moves = MoveGenerator(current_state).get_detailed_solution_moves(current_state)
                final_memory = get_memory_usage_mb()
                return SearchResult(
                    success=True,
                    solution=solution_moves,
                    states_explored=self.states_explored,
                    time_taken=time.time() - start_time,
                    final_state=current_state,
                    memory_used_mb=final_memory - initial_memory,
                )
            
            # Generate successor states.
            move_generator = MoveGenerator(current_state)
            successors = move_generator.get_successor_states()
            
            for successor in successors:
                self.states_generated += 1
                
                # Skip if deadlock detected.
                if self.use_deadlock_detection and detect_deadlock(successor):
                    self.deadlocks_detected += 1
                    continue
                
                # Calculate costs.
                successor.g_cost = current_state.g_cost + 1  # Each move has cost 1.
                successor.h_cost = self.heuristic_func(successor)
                successor.f_cost = successor.g_cost + successor.h_cost
                
                successor_key = successor.get_state_key()
                
                # Skip if we've seen this state with better cost.
                if (successor_key in state_costs and 
                    state_costs[successor_key] <= successor.g_cost):
                    self.duplicate_states += 1
                    continue
                
                # Skip if already in closed set with better cost.
                if successor_key in closed_set:
                    continue
                
                # Update best known cost and add to open list.
                state_costs[successor_key] = successor.g_cost
                heapq.heappush(open_list, 
                              (successor.f_cost, self.states_generated, successor))
        
        # No solution found.
        final_memory = get_memory_usage_mb()
        return SearchResult(
            success=False,
            states_explored=self.states_explored,
            time_taken=time.time() - start_time,
            error_message="No solution exists (open list exhausted)",
            memory_used_mb=final_memory - initial_memory,
        )

class SokobanAStar:
    """Main interface for Sokoban A* solving."""
    
    def __init__(self):
        self.solver = None
        self.last_result = None
    
    def solve_puzzle(self, matrix: List[List[str]],
                    max_states: int = 100000,
                    max_time: float = 300.0,
                    use_deadlock_detection: bool = True) -> SearchResult:
        """
        Solve a Sokoban puzzle from matrix representation.
        
        Args:
            matrix: 2D list representing the puzzle.
            max_states: Maximum states to explore.
            max_time: Maximum solving time in seconds.
            use_deadlock_detection: Enable deadlock pruning.
            
        Returns:
            SearchResult with solution and statistics.
        """

        try: 
            from sokoban_state import create_initial_state
            initial_state = create_initial_state(matrix)
            
            # Create solver and solve
            self.solver = AStarSolver(
                max_states=max_states,
                max_time=max_time,
                use_deadlock_detection=use_deadlock_detection
            )
            
            self.last_result = self.solver.solve(initial_state)
            
            return self.last_result
        
        except Exception as e:
            error_result = SearchResult(
                success=False,
                error_message=f"Error during solving: {str(e)}",
                memory_used_mb=0.0,
            )
            self.last_result = error_result
            return error_result