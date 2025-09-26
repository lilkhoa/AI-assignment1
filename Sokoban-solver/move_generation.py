"""
Move Generation
"""

from typing import List, Tuple, Set
from collections import deque
from sokoban_state import State, AStarState

class MoveGenerator:
    """Generates valid moves and successor states for Sokoban."""
    
    # Movement directions: up, down, left, right.
    DIRECTIONS = [
        (0, -1, 'U'),  # Up.
        (0, 1, 'D'),   # Down.
        (-1, 0, 'L'),  # Left.
        (1, 0, 'R')    # Right.
    ]
    
    def __init__(self, state: State):
        """Initialize with current state."""
        self.state = state
        self.matrix = state.matrix
        self.boxes = state.box_positions
        self.goals = state.goal_positions
    
    def get_successor_states(self) -> List[State]:
        """
        Generate all valid successor states from current state.
        
        Returns:
            List of valid successor State objects of the same type as input.
        """
        successors = []
        
        # Generate all possible pushes.
        push_moves = self._generate_push_moves()
        
        for move in push_moves:
            successor = self._apply_push_move(move)
            if successor:
                successors.append(successor)
        
        return successors
    
    def _generate_push_moves(self) -> List[Tuple]:
        """
        Generate all valid push moves from current position.
        
        Returns:
            List of tuples: (box_pos, direction, new_box_pos, player_push_pos).
        """
        valid_moves = []
        player_reachable = self._get_player_reachable_positions()
        
        for box_pos in self.boxes:
            box_x, box_y = box_pos
            
            # Check each direction the box can be pushed.
            for dx, dy, direction in self.DIRECTIONS:
                # Position where box would move to.
                new_box_x = box_x + dx
                new_box_y = box_y + dy
                new_box_pos = (new_box_x, new_box_y)
                
                # Position player needs to be at to push the box.
                player_push_x = box_x - dx
                player_push_y = box_y - dy
                player_push_pos = (player_push_x, player_push_y)
                
                # Check if push is valid.
                if self._is_valid_push(new_box_pos, player_push_pos, player_reachable):
                    valid_moves.append((box_pos, direction, new_box_pos, player_push_pos))
        
        return valid_moves
    
    def _is_valid_push(self, new_box_pos: Tuple[int, int], 
                      player_push_pos: Tuple[int, int], 
                      player_reachable: Set[Tuple[int, int]]) -> bool:
        """
        Check if a push move is valid.
        
        Args:
            new_box_pos: Where the box would move to.
            player_push_pos: Where player needs to be to push.
            player_reachable: Set of positions player can reach.
            
        Returns:
            bool: True if push is valid.
        """
        # Check if new box position is valid (not wall, not occupied by another box).
        if not self._is_valid_box_position(new_box_pos):
            return False
        
        # Check if player can reach the push position.
        if player_push_pos not in player_reachable:
            return False
        
        return True
    
    def _is_valid_box_position(self, pos: Tuple[int, int]) -> bool:
        """Check if position is valid for a box."""
        x, y = pos
        
        # Check bounds.
        if not (0 <= y < len(self.matrix) and 0 <= x < len(self.matrix[y])):
            return False
        
        # Check if position is wall.
        if self.matrix[y][x] == '#':
            return False
        
        # Check if position is occupied by another box.
        if pos in self.boxes:
            return False
        
        return True
    
    def _get_player_reachable_positions(self) -> Set[Tuple[int, int]]:
        """
        Calculate all positions the player can reach. 
        
        Returns:
            Set of reachable positions.
        """
        start_pos = self.state.player_pos
        reachable = set()
        queue = deque([start_pos])
        visited = {start_pos}
        
        while queue:
            current_pos = queue.popleft()
            reachable.add(current_pos)
            
            x, y = current_pos
            
            # Check all four directions.
            for dx, dy, _ in self.DIRECTIONS:
                new_x, new_y = x + dx, y + dy
                new_pos = (new_x, new_y)
                
                # Skip if already visited.
                if new_pos in visited:
                    continue
                
                # Skip if out of bounds.
                if not (0 <= new_y < len(self.matrix) and 0 <= new_x < len(self.matrix[new_y])):
                    continue
                
                # Skip if wall.
                if self.matrix[new_y][new_x] == '#':
                    continue
                
                # Skip if box is there.
                if new_pos in self.boxes:
                    continue
                
                # Add to queue and mark as visited.
                queue.append(new_pos)
                visited.add(new_pos)
        
        return reachable
    
    def _apply_push_move(self, move: Tuple) -> AStarState:
        """
        Apply a push move and create new successor state.
        
        Args:
            move: Tuple (old_box_pos, direction, new_box_pos, player_push_pos).
            
        Returns:
            New SokobanState or None if move is invalid.
        """
        old_box_pos, direction, new_box_pos, player_push_pos = move
        
        # Create new box positions set.
        new_boxes = set(self.boxes)
        new_boxes.remove(old_box_pos)
        new_boxes.add(new_box_pos)
        
        # Create new state.
        new_state = AStarState(
            matrix=self.matrix,
            player_pos=old_box_pos,  # Player moves to where box was.
            box_positions=new_boxes,
            goal_positions=self.goals
        )
        
        # Set move information.
        new_state.move_action = direction
        new_state.parent = self.state
        
        return new_state
    
    def get_solution_path(self, goal_state: State) -> List[str]:
        """
        Extract solution path from goal state by following parent pointers.
        
        Args:
            goal_state: The solved state.
            
        Returns:
            List of move directions leading to solution.
        """
        path = []
        current = goal_state
        
        # Trace back through parent states
        while current.parent is not None:
            if current.move_action:
                path.append(current.move_action)
            current = current.parent
        
        # Reverse to get forward path.
        path.reverse()
        return path
    
    def get_detailed_solution_with_player_moves(self, goal_state: State) -> List[str]:
        """
        Extract detailed solution path including all player movement steps.
        
        Args:
            goal_state: The solved state.
            
        Returns:
            List of individual move directions including player positioning moves.
        """
        # Get the high-level solution (push moves only).
        push_solution = self.get_detailed_solution(goal_state)
        detailed_moves = []
        
        # For each push move, calculate the player path to get there.
        for i, (move_action, state) in enumerate(push_solution):
            if i == 0:  # Initial state.
                continue
                
            parent_state = state.parent
            if parent_state is None:
                continue
                
            # Find which box was pushed and calculate player path.
            player_path = self._calculate_player_path_for_push(parent_state, state, move_action)
            detailed_moves.extend(player_path)
        
        return detailed_moves
    
    def _calculate_player_path_for_push(self, from_state: State, to_state: State, push_direction: str) -> List[str]:
        """
        Calculate the detailed path the player needs to take to perform a push.
        
        Args:
            from_state: State before the push.
            to_state: State after the push.
            push_direction: Direction of the box push.
            
        Returns:
            List of individual player moves including positioning and push.
        """
        # Find which box was moved.
        from_boxes = from_state.box_positions
        to_boxes = to_state.box_positions
        
        # Find the box that moved.
        moved_from = from_boxes - to_boxes
        moved_to = to_boxes - from_boxes
        
        if not moved_from or not moved_to:
            return [push_direction]  # Fallback.
        
        box_from = list(moved_from)[0]
        box_to = list(moved_to)[0]
        
        # Calculate where player needed to be to push.
        direction_map = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
        dx, dy = direction_map[push_direction]
        player_push_pos = (box_from[0] - dx, box_from[1] - dy)
        
        # Calculate player path from current position to push position.
        player_moves = self._find_player_path(from_state, from_state.player_pos, player_push_pos)
        
        # Add the push move.
        player_moves.append(push_direction)
        
        return player_moves
    
    def _find_player_path(self, state: State, start_pos: Tuple[int, int], target_pos: Tuple[int, int]) -> List[str]:
        """
        Find the shortest path for player to move from start to target position.
        
        Args:
            state: Current game state (for obstacle checking).
            start_pos: Player's starting position.
            target_pos: Player's target position.
            
        Returns:
            List of movement directions to reach target.
        """
        if start_pos == target_pos:
            return []
        
        # BFS to find shortest path.
        queue = deque([(start_pos, [])])
        visited = {start_pos}
        
        while queue:
            current_pos, path = queue.popleft()
            
            if current_pos == target_pos:
                return path
            
            x, y = current_pos
            
            # Try all four directions.
            for dx, dy, direction in self.DIRECTIONS:
                new_x, new_y = x + dx, y + dy
                new_pos = (new_x, new_y)
                
                # Skip if already visited.
                if new_pos in visited:
                    continue
                
                # Skip if out of bounds.
                if not (0 <= new_y < len(state.matrix) and 0 <= new_x < len(state.matrix[new_y])):
                    continue
                
                # Skip if wall.
                if state.matrix[new_y][new_x] == '#':
                    continue
                
                # Skip if box is there.
                if new_pos in state.box_positions:
                    continue
                
                # Add to queue with updated path.
                new_path = path + [direction]
                queue.append((new_pos, new_path))
                visited.add(new_pos)
        
        # No path found.
        return []
    
    def get_detailed_solution(self, goal_state: State) -> List[Tuple[str, State]]:
        """
        Get detailed solution with states and moves.
        
        Args:
            goal_state: The solved state.
            
        Returns:
            List of (move, state) tuples.
        """
        solution = []
        current = goal_state
        
        # Trace back through parent states.
        while current.parent is not None:
            solution.append((current.move_action, current))
            current = current.parent
        
        # Add initial state.
        solution.append((None, current))
        
        # Reverse to get forward path.
        solution.reverse()
        return solution

def generate_moves(state: AStarState) -> List[AStarState]:
    """
    Convenience function to generate successor states.
    
    Args:
        state: Current AStarState.
        
    Returns:
        List of successor states.
    """
    generator = MoveGenerator(state)
    return generator.get_successor_states()

def get_solution_moves(goal_state: State) -> List[str]:
    """
    Convenience function to extract solution path (push moves only).
    
    Args:
        goal_state: Solved state.
        
    Returns:
        List of move directions (push moves only).
    """
    generator = MoveGenerator(goal_state)
    return generator.get_solution_path(goal_state)

def get_detailed_solution_moves(goal_state: State) -> List[str]:
    """
    Convenience function to extract detailed solution path with all player movements.
    
    Args:
        goal_state: Solved state.
        
    Returns:
        List of all move directions including player positioning moves.
    """
    generator = MoveGenerator(goal_state)
    return generator.get_detailed_solution_with_player_moves(goal_state)

def apply_single_move(state, move_direction):
        """
        Apply a single move to the state and return new state.
        This function is used for animation.
        
        Args:
            state: Current SokobanState.
            move_direction: Direction to move ('U', 'D', 'L', 'R').
            
        Returns:
            New SokobanState after applying the move, or None if invalid.
        """
        # Direction mappings.
        direction_map = {
            'U': (0, -1),
            'D': (0, 1), 
            'L': (-1, 0),
            'R': (1, 0)
        }
        
        if move_direction not in direction_map:
            return None
        
        dx, dy = direction_map[move_direction]
        player_x, player_y = state.player_pos
        new_player_x = player_x + dx
        new_player_y = player_y + dy
        new_player_pos = (new_player_x, new_player_y)
        
        # Check if new position is valid.
        if not (0 <= new_player_y < len(state.matrix) and 0 <= new_player_x < len(state.matrix[new_player_y])):
            return None
        
        # Check if new position is a wall.
        if state.matrix[new_player_y][new_player_x] == '#':
            return None
        
        new_boxes = set(state.box_positions)
        
        # Check if there's a box at the new position.
        if new_player_pos in state.box_positions:
            # Player is pushing a box.
            box_new_x = new_player_x + dx
            box_new_y = new_player_y + dy
            box_new_pos = (box_new_x, box_new_y)
            
            # Check if box can be pushed.
            if not (0 <= box_new_y < len(state.matrix) and 0 <= box_new_x < len(state.matrix[box_new_y])):
                return None  # Box would go out of bounds.
                
            if state.matrix[box_new_y][box_new_x] == '#':
                return None  # Box would hit wall.
                
            if box_new_pos in state.box_positions:
                return None  # Box would hit another box.
            
            # Move the box.
            new_boxes.remove(new_player_pos)
            new_boxes.add(box_new_pos)
        
        # Create new state
        new_state = AStarState(
            matrix=state.matrix,
            player_pos=new_player_pos,
            box_positions=new_boxes,
            goal_positions=state.goal_positions
        )
        
        return new_state