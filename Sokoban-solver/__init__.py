"""
Sokoban A* Solver Package
"""

from .astar_solver import solve_sokoban, solve_level, SokobanAStar, SearchResult
from .sokoban_state import State, AStarState, SokobanState, create_initial_state
from .heuristics import SokobanHeuristics, get_heuristic_function
from .deadlock_detection import DeadlockDetector, detect_deadlock
from .move_generation import MoveGenerator, generate_moves

__author__ = "lilkhoa"

# Export main functions for easy access
__all__ = [
    'SokobanAStar',
    'SearchResult',
    'State',
    'AStarState', 
    'create_initial_state',
    'SokobanHeuristics',
    'get_heuristic_function',
    'DeadlockDetector',
    'detect_deadlock',
    'MoveGenerator',
    'generate_moves',
]