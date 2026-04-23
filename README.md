# PathFinder
AI Pathfinder
Overview

AI Pathfinder is an interactive visualization tool designed to demonstrate how classical AI pathfinding algorithms operate in a grid-based environment. Instead of relying on static output, this project allows users to observe how algorithms explore and solve a problem in real time.

The goal of this project was to better understand how different algorithms behave, especially in terms of node exploration, efficiency, and decision-making. As a visual learner, building this system made it significantly easier to understand how each algorithm processes the grid and reaches a solution.

Features
Interactive grid-based environment
Multiple pathfinding algorithms:
Breadth-First Search (BFS)
Greedy Best-First Search
Uniform Cost Search (UCS)
Iterative Deepening Search (IDS)
A*
Weighted A*
Random solvable map generation
Real-time visualization of node exploration
Heatmap-style visualization (work in progress)
Adjustable speed controls
UI-based interaction (no command line arguments needed)
Technologies Used
Python
Pygame
Core Libraries
heapq – priority queue (used in UCS, A*)
collections.deque – queue implementation (used in BFS)
random, os, datetime – map generation and system handling
How It Works

The system generates a random grid with obstacles while ensuring that a valid path exists between the start and goal nodes. This allows all algorithms to be tested under consistent conditions.

Each algorithm explores the grid differently:

BFS and UCS explore broadly and guarantee optimal paths
Greedy and Weighted A* prioritize speed using heuristics
A* balances both optimality and efficiency

The visualization updates in real time, showing how nodes are explored and how each algorithm approaches the solution.

Running the Project
1. Install dependencies
pip install pygame
2. Run the program
python main.py

Once the program is running, all functionality is handled through the UI.

Observations
BFS and UCS guarantee optimal paths, but explore many nodes
Greedy and Weighted A* are faster but may produce suboptimal paths
A* provides the best balance between performance and correctness
UCS can be noticeably slower during the initial exploration phase
Future Improvements
Improve the heatmap to accurately track node visit frequency
Add detailed performance logging (runtime, node expansions)
Optimize algorithm performance, especially UCS
Explore alternative procedural map generation techniques
Further refine UI layout and usability
