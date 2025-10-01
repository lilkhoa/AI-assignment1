"""
Sokoban A* Solver Main File.
"""

import sys
import os
import argparse
import time
from typing import List

# Add the parent directory to path for imports.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astar_solver import SokobanAStar, SearchResult
from sokoban_state import create_initial_state
from move_generation import get_detailed_solution_moves, apply_single_move

def load_level_from_original_format(level_path: str) -> List[List[str]]:
    """
    Load level from original pySokoban format.
    
    Args:
        level_path: Path to level file.
        
    Returns:
        2D matrix representation.
    """
    try:
        with open(level_path, 'r') as f:
            lines = f.readlines()
        
        matrix = []
        for line in lines:
            # Remove newline but preserve spaces for proper level structure.
            row = list(line.rstrip('\n'))
            if row:  # Skip empty lines.
                matrix.append(row)
        
        return matrix
    except Exception as e:
        print(f"Error loading level: {e}")
        return None

def print_level(matrix: List[List[str]], level_name: str = ""):
    """Print level in readable format."""
    print(f"Level {level_name}: ")
    for row in matrix:
        print(''.join(row))
    print()

def print_solution_animation(result: SearchResult, delay: float = 0.5, detailed: bool = False, initial_matrix: List[List[str]] = None):
    """
    Print animated solution showing each step
    
    Args:
        result: Search result containing solution
        delay: Delay between steps in seconds
        detailed: If True, show all player movement steps; if False, show only push moves
        initial_matrix: Initial board matrix (needed for detailed animation)
    """
    if not result.success or not result.final_state:
        print("No solution to animate")
        return
    
    if detailed and initial_matrix:
        # Show detailed solution with all player movements
        detailed_moves = get_detailed_solution_moves(result.final_state)
        
        # Apply moves step by step
        state = create_initial_state(initial_matrix)
        
        print("Initial State:")
        state.print_state()
        
        # Apply each detailed move
        for i, move in enumerate(detailed_moves):
            # Apply the move
            new_state = apply_single_move(state, move)
            
            if new_state:
                state = new_state
                state.print_state()
                
                if delay > 0 and i < len(detailed_moves) - 1:
                    time.sleep(delay)
            else:
                break
            
    else:
        from move_generation import MoveGenerator
        generator = MoveGenerator(result.final_state)
        detailed_solution = generator.get_detailed_solution(result.final_state)
        
        for i, (move, state) in enumerate(detailed_solution):
            state.print_state()
            
            if delay > 0 and i < len(detailed_solution) - 1:
                time.sleep(delay)

def store_solution(level_matrix: List[List[str]], result: SearchResult, level_name: str):
    """
    Store the detailed solution moves into a file in pySokoban format.
    We store the level in the pySokoban directory for rendering as well.
    
    Args:
        result: SearchResult containing the solution.
        level_name: Name of the level to create the file for.
    """
    if not result.success or not result.final_state:
        print('No solution to store')
        return
    
    # Get detailed moves
    detailed_moves = get_detailed_solution_moves(result.final_state)
    
    # Store the solution in the ./result directory
    level_mode = level_name.split('_')[0]  # Extract mode from level name
    level_dir = f'./results/{level_mode}'
    os.makedirs(level_dir, exist_ok=True)
    result_file_path = f'./results/{level_mode}/{level_name}_solution.txt'
    try:
        with open(result_file_path, 'w') as f:
            f.write(''.join(detailed_moves))
            print(f'Solution stored in {result_file_path}')
    except Exception as e:
        print(f'Error storing solution: {e}')


    # This one is for rendering
    # Create file path
    file_path = '../pySokoban/levels/solver/{}.txt'.format(level_name)
    try:
        with open(file_path, 'w') as f:
            f.write(''.join(detailed_moves))
    except Exception as e:
        print(f"Error storing solution: {e}")

    # Store the level matrix
    level_file_path = '../pySokoban/levels/test/{}.txt'.format(level_name)
    try:
        with open(level_file_path, 'w') as f:
            for row in level_matrix:
                f.write(''.join(row) + '\n')
    except Exception as e:
        print(f"Error storing solution: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Sokoban A* Solver")
    parser.add_argument("--mode", choices=["easy", "medium", "hard"], default="easy",
                          help="Difficulty mode for level selection")
    parser.add_argument("--level", help="Specific level file to solve")
    parser.add_argument("--max-states", type=int, default=10000000,
                       help="Maximum states to explore")
    parser.add_argument("--max-time", type=float, default=30000.0,
                       help="Maximum time in seconds")
    parser.add_argument("--no-deadlock", action="store_true",
                       help="Disable deadlock detection")
    
    args = parser.parse_args()

    level_to_solve = f"test_level/{args.mode}/{args.mode}_{args.level}.txt"
    level_name = f"{args.mode}_{args.level}"

    if not os.path.exists(level_to_solve):
        print(f"Level file not found: {level_to_solve}")
        return

    matrix = load_level_from_original_format(level_to_solve)
    if matrix is None:
        return
    
    print_level(matrix, level_name)
    
    solver = SokobanAStar()
    result = solver.solve_puzzle(
        matrix,
        max_states=args.max_states,
        max_time=args.max_time,
        use_deadlock_detection=not args.no_deadlock,
    )

    result.solution = get_detailed_solution_moves(result.final_state) if result.success else []
    print(result)
    store_solution(matrix, result, level_name=level_name)

if __name__ == "__main__":
    main()