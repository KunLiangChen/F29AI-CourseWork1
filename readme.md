# F29AI Course Work 1

This is an implementation of the F29AI coursework 1(Heriot-Watt University, 2025) of the group 11. The project consists of two independent projects: a **Sudoku Solver** with GUI and a **Lunar Mission Planner** using PDDL to plan.

##  Project Overview

This repository consists of two independent projects developed as part of the F29AI (Artificial Intelligence) course at Heriot-Watt University:

### 1. **Sudoku Solver** 
An backtrack based Sudoku puzzle solver with a modern PyQt5 GUI, featuring CSP (Constraint Satisfaction Problem) solving with advanced heuristics and constraint propagation.

### 2. **MoonSong - Lunar Mission Planner** 
An automated planning system written in PDDL (Planning Domain Definition Language) that solves lunar rover missions using STRIPS planning.





---

##  Project 1: Sudoku Solver


### Key Features

####  Solver Algorithms
- **CSP Solver**: Constraint satisfaction using backtracking search
- **Variable Selection**: Minimum Remaining Values (MRV) heuristic
- **Value Ordering**: Least Constraining Value (LCV) heuristic and Degree heuristic
- **Inference**: Forward checking 
- **Domain Management**: Maintains possible values for each cell

####  GUI Components
- **Board Widget**: 9x9 interactive Sudoku grid with dark theme
- **Visualization**: Cell highlighting
- **Control Panel**: Load, Save, Solve, Reset, and Quit buttons
- **Progress Display**: Real-time metrics and step-by-step logs
- **3x3 Box Separators**: Custom painting for Sudoku grid structure

#### Core Modules

| Module | Purpose |
|--------|---------|
| `board.py` | SudokuBoard class with validation methods |
| `csp_solver.py` | Main CSP solver with backtracking |
| `heuristics.py` | MRV/LCV variable ordering strategies |
| `inference.py` | Forward checking and AC-3 algorithms |
| `metrics.py` | Performance tracking and statistics |
| `file_io.py` | Load/save puzzle files |

### Usage

#### Installation

```bash
# Create your own virtual environment for solver (or choose a existing one)
# Install dependency
pip install requirement.txt
# Navigate to sudoku_solver directory
cd sudoku_solver
```

#### Running the Application

```bash
python main.py
```

#### Loading a Puzzle

1. Click **"Load (.txt/.csv)"** button
2. Select a puzzle file from `data/` folder
3. Board will display the puzzle

#### Solving

1. Click **"Solve"** button
2. Solver runs in background (UI remains responsive)
3. Watch step-by-step progress in the logs
4. Final solution displays with metrics

#### Saving

1. Click **"Save"** button
2. Choose location and filename
3. Solution exported to file

### Puzzle File Format

**TXT Format** (space or comma-separated):
```
8 0 0 0 0 0 0 0 0
0 0 3 6 0 0 0 0 0
0 7 0 0 9 0 2 0 0
0 5 0 0 0 7 0 0 0
0 0 0 0 4 5 9 0 0
0 0 0 1 0 0 0 3 0
0 0 1 0 0 0 0 6 8
0 0 8 5 0 0 0 1 0
0 9 0 0 0 0 4 0 0

or

5 3 . . 7 . . . .
6 . . 1 9 5 . . .
. 9 8 . . . . 6 .
8 . . . 6 . . . 3
...
```

**CSV Format** (comma-separated):
```
5,3,.,.,7,.,.,.,.,
6,.,.,1,9,5,.,.,.,
.,9,8,.,.,.,.,6,.
...
```

Use `0` or `.` for empty cells.

### Sample Puzzles

Available in `data/` directory:
- `easy.txt` - Beginner level
- `medium.txt` - Intermediate level
- `hard.txt` - Advanced level
- `extreme.txt` - Expert level

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_csp_solver.py -v
```

---

##  Project 2: MoonSong - Lunar Mission Planner
![Song of the Welkin Moon](Moon.png)

***From Genshin impact***
### Overview

An automated planning system that solves lunar rover missions using **PDDL (Planning Domain Definition Language)** and **STRIPS planning formalism**.

### Mission Overview

The system solves three increasingly complex lunar missions:

| Mission | Complexity | Tasks |
|---------|-----------|-------|
| **Mission 1** | Basic | Deploy rover, collect sample, return |
| **Mission 2** | Intermediate | Multiple locations, multi-data collection |
| **Mission 3** | Advanced | Extended domain, complex constraints |

### PDDL Structure

#### Domain Definition (`domain.pddl` / `domain-ext.pddl`)

**Types**:
- `rover` - Lunar exploration vehicle
- `lander` - Landing platform
- `location` - Waypoint on lunar surface
- `data` - Sensory information (scan, image)
- `sample` - Physical material collection

**Key Actions**:
- `move-rover` - Navigate between connected locations
- `take-image` - Capture visual data
- `take-scan` - Perform ground analysis
- `collect-sample` - Gather physical samples
- `communicate` - Transfer data via lander

**Constraints**:
- Memory limitations for rover
- Hand capacity for sample collection
- Movement restricted to connected locations
- Data transfer requires lander presence

#### Problem Definition (Mission Files)

Each mission specifies:
- **Objects**: Rovers, landers, locations, data types
- **Initial State**: Starting configuration and relationships
- **Goals**: Objectives to achieve

### Example: Mission 1

```pddl
(define (problem lunar-mission-1)
    (:domain lunar)

    (:objects
        rover - rover
        lander - lander
        WP1 - location
        WP2 - location
        WP3 - location
        WP4 - location
        WP5 - location
        image - image
        scan - scan
        sample - sample
    )

    (:init
        (not (is_landed lander))
        (not (is_deployed rover))
        (is_connected WP1 WP2)
        (is_connected WP1 WP4)
        (is_connected WP2 WP3)
        (is_connected WP3 WP5)
        (is_connected WP4 WP3)
        (is_connected WP5 WP1)
        (need_image WP5 image)
        (need_scan WP3 scan)
        (need_sample WP1 sample)
        (empty_memory rover)
        (hand_empty rover)
        (association lander rover)

    )

    (:goal
        (and
            (has_received image)
            (has_received scan)
            (sample_got sample)
        )
    )
)
```

### Solution Plans

Each mission has a corresponding `.plan` file containing the sequence of actions to achieve the goal:

```
0.00000: (lander_land lander rover wp1)
0.00100: (take_sample rover wp1 sample)
0.00200: (sample_receive lander rover sample wp1)
0.00300: (rover_move wp1 wp2 rover)
0.00400: (rover_move wp2 wp3 rover)
0.00500: (take_scan rover wp3 scan)
0.00600: (rover_move wp3 wp5 rover)
0.00700: (transmit_data rover scan lander)
0.00800: (take_picture rover wp5 image)
0.00900: (transmit_data rover image lander)
```

### Project Organization

- **PartAB**: Basic planning domains and two introductory missions
- **PartC**: Extended domain with additional constraints and complex planning


---

##  Technologies & Dependencies

### Sudoku Solver
- **Python 3.7+**
- **PyQt5** - GUI framework
- **NumPy** - Array operations and mathematics
- **pytest** - Unit testing framework

### MoonSong
- **PDDL** - Planning domain specification
- **STRIPS** - Planning formalism
- Compatible with:
  - Lama-First
  - BFWS - FF

*Note: Different compiler would generate different plan, this is normal. All the plan in this project are gennerated by Lama-First.*


---



##  Learning Outcomes

### Sudoku Solver
- CSP problem formulation and solving techniques
- Advanced search heuristics
- Constraint propagation algorithms
- GUI design with PyQt5
- Multithreaded programming
- Performance optimization

### MoonSong
- Automated planning fundamentals
- PDDL syntax and semantics
- STRIPS planning formalism
- Domain modeling
- Problem decomposition
- Action-based reasoning

---

##  References & Resources

### Sudoku Solving
- Russell & Norvig: "Artificial Intelligence: A Modern Approach"
- CSP: Chapters 6-7
- Backtracking and heuristics
- Constraint propagation techniques

### Planning
- Planning Domain Definition Language (PDDL)
- STRIPS (Stanford Research Institute Problem Solver)
- Fast Downward Planner Documentation
- Planning algorithms and complexity

### PyQt5
- Official PyQt5 Documentation
- Qt Designer for UI layout
- Signal/slot mechanism
- Threading best practices

---


##  License

This project is part of Heriot-Watt University coursework. All rights reserved for educational purposes.

---

##  Author

### Group 11:

**KunLiang Chen**

**KagamineRia**

---
**Last Updated**: November 2025  
**Status**: Complete and Tested 
