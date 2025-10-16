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
from astar_solver import SearchResult, get_memory_usage_mb
from sokoban_state import DFSState 
class DFSSolver:
    """A* search algorithm implementation for Sokoban."""
    
    def __init__(self, max_states: int = 100000, max_time: float = 300.0, use_deadlock_detection: bool = True):
        """
        Initialize A* solver with configuration.
        
        Args:
            heuristic_name: Name of heuristic function to use.
            max_states: Maximum states to explore before giving up.
            max_time: Maximum time in seconds before timeout.
            use_deadlock_detection: Whether to use deadlock pruning.
        """

        self.max_states = max_states
        self.max_time = max_time
        self.use_deadlock_detection = use_deadlock_detection
        
        
        self.states_explored = 0
        self.states_generated = 0
        self.deadlocks_detected = 0
        self.duplicate_states = 0
        
    def solve(self, initial_state: DFSState) -> SearchResult: 
        """
        
        """
        start_time = time.time()
        initial_memory = get_memory_usage_mb()
        
       
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
        stack=[initial_state]
        closed_set = set()
        while stack:
            if time.time() - start_time > self.max_time:
                final_memory = get_memory_usage_mb()
                return SearchResult(
                    success=False,
                    states_explored=self.states_explored,
                    time_taken=time.time() - start_time,
                    error_message=f"Timeout after {self.max_time}s",
                    memory_used_mb=final_memory - initial_memory,
                )
            
            # Check limit 
            if self.states_explored >= self.max_states:
                final_memory = get_memory_usage_mb()
                return SearchResult(
                    success=False,
                    states_explored=self.states_explored,
                    time_taken=time.time() - start_time,
                    error_message=f"State limit reached ({self.max_states})",
                    memory_used_mb=final_memory - initial_memory,
                )
            
            # Pop 
            current_state = stack.pop()
            state_key = current_state.get_state_key()
            
            if state_key in closed_set:
                continue
            
            # check visited
            closed_set.add(state_key)
            self.states_explored += 1
            
            # Check  goal 
            if current_state.is_goal_state():
                solution_moves = MoveGenerator(current_state).get_solution_path(current_state)
                final_memory = get_memory_usage_mb()
                return SearchResult(
                    success=True,
                    solution=solution_moves,
                    states_explored=self.states_explored,
                    time_taken=time.time() - start_time,
                    final_state=current_state,
                    memory_used_mb=final_memory - initial_memory,
                )
            
            # Generate  states.
            move_generator = MoveGenerator(current_state)
            successors = move_generator.get_successor_states()
            
            for successor in successors:
                self.states_generated += 1
                
                # Skip if deadlock detected.
                if self.use_deadlock_detection and detect_deadlock(successor):
                    self.deadlocks_detected += 1
                    continue
                
                successor_key = successor.get_state_key()
                
                if successor_key in closed_set:
                    self.duplicate_states += 1
                    continue
                
                # Push 
                stack.append(successor)
        
        # No solution found.
        final_memory = get_memory_usage_mb()
        return SearchResult(
            success=False,
            states_explored=self.states_explored,
            time_taken=time.time() - start_time,
            error_message="No solution exists (stack exhausted)",
            memory_used_mb=final_memory - initial_memory,
        )
    
    def get_statistics(self) -> Dict:
        """Get detailed search statistics."""
        return {
            'states_explored': self.states_explored,
            'states_generated': self.states_generated,
            'deadlocks_detected': self.deadlocks_detected,
            'duplicate_states': self.duplicate_states,
            'deadlock_pruning_enabled': self.use_deadlock_detection
        }
###############################################################################################################
class SokobanDFS:
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
            heuristic: Heuristic function name.
            max_states: Maximum states to explore.
            max_time: Maximum solving time in seconds.
            use_deadlock_detection: Enable deadlock pruning.
            verbose: Print progress information.
            
        Returns:
            SearchResult with solution and statistics.
        """

        try: 
            from sokoban_state import create_initial_state
            initial_state = create_initial_state(matrix)
            
            # Create solver and solve
            self.solver = DFSSolver(
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