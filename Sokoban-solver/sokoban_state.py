"""
Sokoban State Representation.
"""

import copy
from typing import List, Tuple, Set

class State:
    """Base class representing a state in the Sokoban game."""
    
    def __init__(self, matrix: List[List[str]], player_pos: Tuple[int, int], 
                 box_positions: Set[Tuple[int, int]], goal_positions: Set[Tuple[int, int]]):
        """
        Initialize a Sokoban state.
        
        Args:
            matrix: 2D grid representing the game board.
            player_pos: (x, y) position of the player.
            box_positions: Set of (x, y) positions of boxes.
            goal_positions: Set of (x, y) positions of goals.
        """
        self.matrix = [row[:] for row in matrix]
        self.player_pos = player_pos
        self.box_positions = frozenset(box_positions)
        self.goal_positions = frozenset(goal_positions)
        self.parent = None
        self.move_action = None  # The move that led to this state.
        
    def __eq__(self, other):
        """Two states are equal if player and box positions are the same."""
        if not isinstance(other, State):
            return False
        return (self.player_pos == other.player_pos and 
                self.box_positions == other.box_positions)
    
    def __hash__(self):
        """Hash based on player position and box positions for efficient storage."""
        return hash((self.player_pos, self.box_positions))
    
    def is_goal_state(self) -> bool:
        """Check if all boxes are on goal positions."""
        return self.box_positions == self.goal_positions
    
    def get_state_key(self) -> Tuple:
        """Get a unique key for this state for closed set storage."""
        return (self.player_pos, self.box_positions)
    
    def copy(self):
        """Create a copy of this state."""
        new_state = self.__class__(self.matrix, self.player_pos, 
                                  self.box_positions, self.goal_positions)
        new_state.parent = self.parent
        new_state.move_action = self.move_action
        return new_state
    
    def get_boxes_not_on_goals(self) -> Set[Tuple[int, int]]:
        """Get positions of boxes that are not on goal positions."""
        return self.box_positions - self.goal_positions
    
    def get_goals_without_boxes(self) -> Set[Tuple[int, int]]:
        """Get goal positions that don't have boxes."""
        return self.goal_positions - self.box_positions
    
    def is_wall(self, x: int, y: int) -> bool:
        """Check if position (x, y) is a wall."""
        if 0 <= y < len(self.matrix) and 0 <= x < len(self.matrix[y]):
            return self.matrix[y][x] == '#'
        return True  # Out of bounds is considered wall.
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position (x, y) is valid (not wall and within bounds)."""
        return (0 <= y < len(self.matrix) and 
                0 <= x < len(self.matrix[y]) and 
                not self.is_wall(x, y))
    
    def print_state(self):
        """Print the current state for debugging."""
        print(f"Player at: {self.player_pos}")
        print(f"Boxes at: {self.box_positions}")
        print("Board:")
        for y, row in enumerate(self.matrix):
            line = ""
            for x, cell in enumerate(row):
                pos = (x, y)
                if pos == self.player_pos:
                    if pos in self.goal_positions:
                        line += "+"  # Player on goal
                    else:
                        line += "@"  # Player
                elif pos in self.box_positions:
                    if pos in self.goal_positions:
                        line += "*"  # Box on goal
                    else:
                        line += "$"  # Box
                elif pos in self.goal_positions:
                    line += "."  # Goal
                else:
                    line += cell  # Wall or space
            print(line)
        print()

class DFSState(State):
    """State class for DFS search."""
    
    def __init__(self, matrix: List[List[str]], player_pos: Tuple[int, int], 
                 box_positions: Set[Tuple[int, int]], goal_positions: Set[Tuple[int, int]]):
        """
        Initialize DFS state.
        
        Args:
            matrix: 2D list representing the Sokoban board.
            player_pos: (x, y) position of the player.
            box_positions: Set of (x, y) box positions.
            goal_positions: Set of (x, y) goal positions.
        """
        super().__init__(matrix, player_pos, box_positions, goal_positions)  
    
    def copy(self):
        """Create a deep copy of this DFS state."""
        new_state = super().copy()
        return new_state

class AStarState(State):
    """State class specifically for A* search"""
    
    def __init__(self, matrix: List[List[str]], player_pos: Tuple[int, int], 
                 box_positions: Set[Tuple[int, int]], goal_positions: Set[Tuple[int, int]]):
        """Initialize A* state"""
        super().__init__(matrix, player_pos, box_positions, goal_positions)
        self.g_cost = 0  # Cost from start
        self.h_cost = 0  # Heuristic cost to goal
        self.f_cost = 0  # Total cost (g + h)
    
    def __lt__(self, other):
        """For priority queue ordering - lower f_cost has higher priority."""
        return self.f_cost < other.f_cost
    
    def copy(self):
        """Create a copy of this A* state."""
        new_state = super().copy()
        new_state.g_cost = self.g_cost
        new_state.h_cost = self.h_cost
        new_state.f_cost = self.f_cost
        return new_state

def create_initial_state(matrix: List[List[str]]) -> State:
    """
    Create initial state from a level matrix.
    
    Args:
        matrix: 2D list representing the level.
        
    Returns:
        State: Initial state of the puzzle.
    """
    player_pos = None
    box_positions = set()
    goal_positions = set()
    clean_matrix = []
    
    # Process the matrix to extract positions and create clean board
    for y, row in enumerate(matrix):
        clean_row = []
        for x, cell in enumerate(row):
            if cell == '@':  # Player
                player_pos = (x, y)
                clean_row.append(' ')
            elif cell == '+':  # Player on goal
                player_pos = (x, y)
                goal_positions.add((x, y))
                clean_row.append(' ')
            elif cell == '$':  # Box
                box_positions.add((x, y))
                clean_row.append(' ')
            elif cell == '*':  # Box on goal
                box_positions.add((x, y))
                goal_positions.add((x, y))
                clean_row.append(' ')
            elif cell == '.':  # Goal
                goal_positions.add((x, y))
                clean_row.append(' ')
            else:  # Wall or space
                clean_row.append(cell)
        clean_matrix.append(clean_row)
    
    if player_pos is None:
        raise ValueError("No player position found in the level")
    
    return State(clean_matrix, player_pos, box_positions, goal_positions)