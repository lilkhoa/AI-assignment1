"""
Heuristic Functions.
"""

from typing import Set, Tuple, List
from collections import deque
import math

class SokobanHeuristics:
    """The heuristic functions for Sokoban puzzle solving."""
    
    @staticmethod
    def _manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    @staticmethod
    def _simple_manhattan_heuristic(state) -> int:
        """
        Simple heuristic: sum of Manhattan distances from each box to the nearest goal.
        Possibly there are 2 boxes with the same nearest goal. 
        """
        if state.is_goal_state():
            return 0
            
        total_distance = 0
        boxes = state.get_boxes_not_on_goals()
        goals = state.get_goals_without_boxes()
        
        for box in boxes:
            min_dist = min(SokobanHeuristics._manhattan_distance(box, goal) for goal in goals)
            total_distance += min_dist
            
        return total_distance
    
    @staticmethod
    def _hungarian_assignment_heuristic(state) -> int:
        """
        Hungarian algorithm-based heuristic for optimal box-goal assignment.
        """
        if state.is_goal_state():
            return 0
            
        boxes = list(state.get_boxes_not_on_goals())
        goals = list(state.get_goals_without_boxes())
        
        if not boxes or not goals:
            return 0

        if len(boxes) <= 4 and len(goals) <= 4:
            return SokobanHeuristics._min_cost_assignment(boxes, goals)
        else:
            return SokobanHeuristics._simple_manhattan_heuristic(state)
    
    @staticmethod
    def _min_cost_assignment(boxes: List[Tuple[int, int]], 
                           goals: List[Tuple[int, int]]) -> int:
        """
        Calculate minimum cost assignment of boxes to goals.
        """
        if not boxes or not goals:
            return 0
            
        min_boxes = min(len(boxes), len(goals))
        min_cost = float('inf')
        
        # Generate all possible permutations of goal assignments.
        from itertools import permutations
        
        for goal_perm in permutations(goals, min_boxes):
            cost = sum(SokobanHeuristics._manhattan_distance(boxes[i], goal_perm[i]) 
                      for i in range(min_boxes))
            min_cost = min(min_cost, cost)
            
        return min_cost if min_cost != float('inf') else 0
    
    @staticmethod
    def our_heuristic(state) -> int:
        """
        Advanced heuristic combining multiple factors:
        1. Box-goal assignment cost.
        2. Player positioning cost.
        3. Penalty for boxes in potential deadlock positions.
        """
        if state.is_goal_state():
            return 0
        
        # Base assignment cost
        base_cost = SokobanHeuristics._hungarian_assignment_heuristic(state)
        
        # Player positioning cost
        player_cost = 0
        boxes = state.get_boxes_not_on_goals()
        if boxes:
            min_player_distance = min(
                SokobanHeuristics._manhattan_distance(state.player_pos, box) 
                for box in boxes
            )
            player_cost = max(0, min_player_distance - 1)
        
        # Deadlock penalty (simple version - boxes in corners without goals)
        deadlock_penalty = SokobanHeuristics._calculate_deadlock_penalty(state)
        
        return base_cost + player_cost + deadlock_penalty
    
    @staticmethod
    def _calculate_deadlock_penalty(state) -> int:
        """
        Calculate penalty for boxes that might be in deadlock positions
        Simple version: check for boxes in corners that are not goals
        """
        penalty = 0
        boxes = state.get_boxes_not_on_goals()
        
        for box_x, box_y in boxes:
            # Check if box is in a corner (not a goal)
            if SokobanHeuristics._is_corner_deadlock(state, box_x, box_y):
                penalty += 100  # High penalty for corner deadlocks
            elif SokobanHeuristics._is_edge_deadlock(state, box_x, box_y):
                penalty += 10   # Lower penalty for potential edge problems
        
        return penalty
    
    @staticmethod
    def _is_corner_deadlock(state, x: int, y: int) -> bool:
        """Check if a box at (x,y) is in a corner deadlock."""
        # If position is a goal, it's not a deadlock
        if (x, y) in state.goal_positions:
            return False
            
        # Check all four corner combinations
        corners = [
            (state.is_wall(x-1, y) and state.is_wall(x, y-1)),  # Top-left
            (state.is_wall(x+1, y) and state.is_wall(x, y-1)),  # Top-right
            (state.is_wall(x-1, y) and state.is_wall(x, y+1)),  # Bottom-left
            (state.is_wall(x+1, y) and state.is_wall(x, y+1))   # Bottom-right
        ]
        
        return any(corners)
    
    @staticmethod
    def _is_edge_deadlock(state, x: int, y: int) -> bool:
        """Check if a box at (x,y) might be in an edge deadlock."""
        # If position is a goal, it's not a deadlock
        if (x, y) in state.goal_positions:
            return False
        
        # Check if box is against a wall with no goals in that direction
        against_wall = False
        no_goals_in_direction = False
        
        # Check horizontal walls
        if state.is_wall(x, y-1) or state.is_wall(x, y+1):
            against_wall = True
            # Check if there are goals in the row
            row_goals = any(goal_y == y for goal_x, goal_y in state.goal_positions)
            if not row_goals:
                no_goals_in_direction = True
        
        # Check vertical walls
        if state.is_wall(x-1, y) or state.is_wall(x+1, y):
            against_wall = True
            # Check if there are goals in the column
            col_goals = any(goal_x == x for goal_x, goal_y in state.goal_positions)
            if not col_goals:
                no_goals_in_direction = True
        
        return against_wall and no_goals_in_direction

def get_heuristic_function():
    """
    Get our heuristic function.
        
    Returns:
        Callable heuristic function
    """
    return SokobanHeuristics.our_heuristic