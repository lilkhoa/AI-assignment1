# 🎮 Sokoban Solver & Visualizer

A comprehensive Sokoban puzzle solver featuring algorithms (A*, DFS) and interactive pygame visualization.

## 🚀 Quick Start

### Prerequisites
```bash
pip install pygame numpy psutil
```

## 📋 Complete Workflow Guide

### Step 1: Prepare Your Level

**Option A: Use Existing Levels**
- Pre-built levels are available in `/Sokoban-solver/test_level/`:
  - `easy` folder - Simple puzzles for testing
  - `medium` folder - Moderate difficulty
  - `hard` folder - Complex challenges

**Option B: Create Custom Level**
1. Create a new `.txt` file in `/Sokoban-solver/test_level/--/` (-- is any difficulty folder).
2. Use standard Sokoban notation, for example:
   ```
   #########
   #@      #    # = Wall
   # $$$...#    @ = Player  
   #    ###     $ = Box
   #    #       . = Target
   ######       * = Box on target
                + = Player on target
   ```
**Note**: If you're going to create a custom level, let's say an easy level, you should name it `easy_X.txt`, where `X` is the level number that does not conflict with existing levels and place it in the `easy` folder.

### Step 2: Run Your Algorithm

```bash
cd Sokoban-solver
python main.py --mode [easy/medium/hard] --level [1/2/3/...] --solver [DFS/AStar]
```
This command will execute the selected algorithm on your specified level.
**Example**:
```bash
python main.py --mode easy --level 1 --solver AStar
```

### Step 3: View Search Results

After running the algorithm, a search result will be printed in the terminal:
```
Solver: [solver name]
Solution found in Xs
States explored: Y
Memory used: Z MB
Solution length: N moves
Solution: [solution string]
```

**Example Search Result**:
```
Solver: AStar
Solution found in 0.01s
States explored: 28
Memory used: 0.19 MB
Solution length: 46 moves
Solution: RRDRULLLDRURRDRULLLDRURRDRULLLDRDDLURURULLLDRR
```

### Step 4: Visualize with pySokoban
You can visualize the solution with the beautiful `pySokoban` interface. To do that, first, you have to change the `current_level` variable in `pySokoban/sokoban.py` to point to your level that you solved in Step 2. Also, you need to change the `solver_type` variable to match the solver you used (e.g., `AStar` or `DFS`). Then, run:

```bash
cd pySokoban
python sokoban.py
```

These commands will:
1. Load your level from `pySokoban/levels/test/`
2. Load the corresponding solution from `pySokoban/levels/solver/`
3. Display the puzzle and animate the solution

**Note**: In the `pySokoban/sokoban.py` file, you can also change the `theme` variable to switch between different visual themes available in the `themes/` folder. Furthermore, by changing the `solver` variable to `False`, you can manually play the game using keyboard controls.

## 📽️ Demo Video
A demo video showcasing the solver and visualizer can be found here:  
* 1. [[Google Drive] Sokoban Solver Demo](https://drive.google.com/file/d/12XrZPIQhNTQ4Qrdrxq3xWw-BZA964XEB/view?usp=sharing)
* 2. [[YouTube] Sokoban Solver Demo](https://youtu.be/LTxmywwiLzs)

## 🙏 Acknowledgements
Many thanks to the creators of [pySokoban](https://github.com/kazantzakis/pySokoban) for providing a fantastic visualization tool. 
