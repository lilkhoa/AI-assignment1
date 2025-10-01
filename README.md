This file is a guide for how to render the Sokoban game and use the Sokoban solver.

Step 1. Install pygame.

Step 2. Place your level file in the pySokoban/levels/test directory. You can see some examples in the pySokoban/levels/test directory.

Step 3. Run your algorithm and place the solution in a file belonging to the pySokoban/levels/solver directory. The content of the file should be a string of characters, representing the player's moves. You can see some examples in the pySokoban/levels/solver directory.

**Note**: The file name of your solution file (in /pySokoban/levels/solver) should be exactly the same as the file name of your level file (in /pySokoban/levels/test). For example, if your level file is test_level_01.txt, your solution file should be test_level_01.txt as well.

Step 4. Run the sokoban.py file in the pySokoban directory and see the result. In order to see your level and solution, you need to set your `current_level` as well as `solver=True` in the sokoban.py file. When the pygame window opens, press any key to start the simulation.

**Note**: You can change this workflow by making changes to the pySokoban/sokoban.py file. 