"""
Deadlock Detection for Sokoban.
"""

from typing import Set, Tuple, List
from collections import deque
from sokoban_state import State, create_initial_state

class DeadlockDetector:
    """Detects deadlocks in Sokoban states."""
    
    def __init__(self, state):
        """Initialize with a Sokoban state."""
        self.state = state
        self.matrix = state.matrix
        self.goals = state.goal_positions
        self.walls_cache = {}
    
    def is_deadlock(self) -> bool:
        """
        Check if the current state contains any deadlocks.
        
        Returns:
            bool: True if deadlock detected, False otherwise.
        """

        # If the state is already a goal state, no deadlock.
        if self.state.is_goal_state():
            return False
        
        boxes = self.state.get_boxes_not_on_goals()
        
        for box in boxes:
            if self._is_simple_deadlock(box):
                return True
        
        if self._is_freeze_deadlock(boxes):
            return True
        
        return False
    
    def _is_simple_deadlock(self, box_pos: Tuple[int, int]) -> bool:
        """
        Check for simple deadlocks - box in corner.
        
        Args:
            box_pos: Position of the box to check.
            
        Returns:
            bool: True if box is in a simple deadlock.
        """
        x, y = box_pos
        
        # If box is on goal, it's not a deadlock.
        if box_pos in self.goals:
            return False
        
        # Corner deadlock
        corner_patterns = [
            (self._is_wall(x-1, y) and self._is_wall(x, y-1)),  # Top-left corner.
            (self._is_wall(x+1, y) and self._is_wall(x, y-1)),  # Top-right corner.
            (self._is_wall(x-1, y) and self._is_wall(x, y+1)),  # Bottom-left corner.
            (self._is_wall(x+1, y) and self._is_wall(x, y+1))   # Bottom-right corner.
        ]
        
        if any(corner_patterns):
            return True
        
        return False
    
    def _is_freeze_deadlock(self, all_boxes: Set[Tuple[int, int]]) -> bool:
        """
        Check for freeze deadlock: doubled boxes.
        
        Args:
            box_pos: Position of the box to check.
            all_boxes: All box positions in current state.
            
        Returns:
            bool: True if box is in a freeze deadlock.
        """

        # Check if box can move in any direction.
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # down, up, right, left.
        
        can_move = False
        for box_pos in all_boxes:
            x, y = box_pos

            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                behind_x, behind_y = x - dx, y - dy

                if (not self._is_wall(new_x, new_y) and 
                    (new_x, new_y) not in all_boxes and
                    not self._is_wall(behind_x, behind_y) and 
                    (behind_x, behind_y) not in all_boxes):
                    can_move = True
                    break

            if can_move:
                break
        # If box cannot move and is not on goal, it's a freeze deadlock.
        return not can_move
    
    def _is_wall(self, x: int, y: int) -> bool:
        """Check if position is a wall (cached for performance)."""
        pos = (x, y)
        if pos not in self.walls_cache:
            if 0 <= y < len(self.matrix) and 0 <= x < len(self.matrix[y]):
                self.walls_cache[pos] = self.matrix[y][x] == '#'
            else:
                self.walls_cache[pos] = True  # Out of bounds is wall.
        return self.walls_cache[pos]

def detect_deadlock(state: State) -> bool:
    """
    Interface for detecting deadlocks in a state.
    
    Args:
        state: State to check.
        
    Returns:
        bool: True if deadlock detected.
    """
    detector = DeadlockDetector(state)
    return detector.is_deadlock()