# Timetable Scheduler - Project Report

## Executive Summary

The **Timetable Scheduler** is a constraint satisfaction problem (CSP) solver designed to automatically generate optimal university course timetables. It intelligently assigns courses, instructors, rooms, and time slots while respecting a comprehensive set of constraints and preferences. The system uses a two-phase approach combining backtracking search with local search optimization to find feasible and high-quality solutions.

---

## 1. Project Overview

### Purpose
To solve the complex university timetabling problem by:
- Assigning course sessions to specific instructors, rooms, and time slots
- Satisfying hard constraints (no conflicts, instructor qualifications, room capacity)
- Minimizing soft constraint violations (instructor preferences, scheduling gaps)
- Producing optimized timetables as CSV exports

### Key Characteristics
- **Problem Domain**: Constraint Satisfaction Problem (CSP)
- **Solution Approach**: Two-phase solver (backtracking + local search)
- **Input Format**: CSV/XLSX files containing courses, instructors, rooms, time slots, and sections
- **Output Format**: CSV timetable and JSON representation
- **Technology Stack**: Python 3 with pandas and openpyxl

### Target Users
- University scheduling administrators
- Educational institutions needing automated timetable generation
- Academic departments managing course allocation

---

## 2. Architecture & Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Input Data (CSV/XLSX)                     │
│  Courses, Instructors, Rooms, TimeSlots, Sections            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
            ┌────────────────────┐
            │   DataLoader       │
            │  (data_loader/)    │
            └────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │  Variable Generator            │
        │  (models/session.py)           │
        │  Creates assignment variables  │
        └────────┬───────────────────────┘
                 │
                 ▼
      ┌──────────────────────────┐
      │  Domain Builder          │
      │  (csp/domain.py)         │
      │  Builds valid domains    │
      └────────┬─────────────────┘
               │
               ▼
    ┌─────────────────────────────────┐
    │  Phase 1: Backtracking Solver   │
    │  (csp/solver_phase1.py)         │
    │  Finds feasible solution        │
    └────────┬────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────┐
    │  Phase 2: Local Search          │
    │  (csp/solver_phase2.py)         │
    │  Optimizes solution quality     │
    └────────┬────────────────────────┘
             │
             ▼
       ┌──────────────────┐
       │  CSV/JSON Export │
       │  (output/)       │
       └──────────────────┘
```

### Core Components

#### 2.1 Data Layer (data_loader/)
- **DataLoader**: Reads CSV and XLSX files from the `Data/` directory
- Parses:
  - Courses (course_id, name, lecture hours, lab hours, lab type)
  - Instructors (instructor_id, name, qualified courses, preferred/not-preferred time slots)
  - Rooms (room_id, capacity, room type, space type)
  - Time Slots (slot_id, day, start/end times)
  - Sections (section_id, department, level, specialization, student count)
  - Available Courses (department-level-specialization course mappings with preferences)

#### 2.2 Model Layer (models/)

**entities.py** - Domain objects:
- `Course`: Course metadata and session requirements
- `Instructor`: Instructor qualifications and schedule preferences
- `Room`: Room capacity and type specifications
- `TimeSlot`: Time slot definitions
- `Section`: Student cohort information
- `AvailableCourse`: Curriculum mapping with instructor preferences

**session.py** - CSP Variables:
- `Session`: A course instance assigned to one or more time slots
- `VariableGenerator`: Creates assignment variables for each course-section combination
  - Accounts for lecture/lab splits based on course configuration
  - Respects group capacity (max 75 students per group)

#### 2.3 CSP Solver Layer (csp/)

**domain.py - Domain Construction**
- `DomainBuilder`: Creates feasible value domains for each variable
- Filters invalid domain values based on:
  - Instructor qualifications for courses
  - Room capacity vs. section size
  - Instructor availability (preferred vs. not-preferred slots)
  - Timeslot sequence validity

**solver_phase1.py - Feasibility Finding**
- `BacktrackingSolver`: Implements backtracking algorithm with constraint checking
- `TimetableState`: Tracks instructor, room, and section schedules
- `Assignment`: Dataclass representing a variable assignment
- Algorithm:
  1. Uses Most Constrained Variable (MCV) heuristic for variable ordering
  2. Uses Least Constraining Value (LCV) heuristic for value ordering
  3. Performs forward checking to prune future domains
  4. Backtracks on constraint violations
  5. Terminates when complete assignment found or search exhausted

**solver_phase2.py - Solution Optimization**
- `CostEvaluator`: Calculates solution penalties for:
  1. **Instructor Preferences**: Penalties for using not-preferred time slots (cost: 5 per violation)
  2. **Schedule Gaps**: Penalties for isolated sessions (cost: 2 per gap)
  3. **Early Morning Classes**: Penalties for very early sessions (cost: 1 per early slot)
  4. **Broken Groups**: Penalties for sessions not assigned to consecutive slots (cost: 3 per break)
- `IterativeSolver`: Local search optimizer using random restart
  - Performs configurable iterations (default: 20,000)
  - Accepts moves that reduce total cost
  - Implements random swaps and reassignments

#### 2.4 Output Layer (output/)
- `save_solution_to_csv()`: Exports timetable to CSV format
- `save_solution_to_json()`: Exports timetable to JSON format
- Formats assignment data for human readability and further processing

### Data Flow

1. **Load Phase**: CSV/XLSX files → Python objects
2. **Generation Phase**: Create CSP variables (assignments to create)
3. **Domain Phase**: Determine valid values for each variable
4. **Solve Phase 1**: Find any feasible solution via backtracking
5. **Solve Phase 2**: Improve solution via local search iterations
6. **Export Phase**: Write results to CSV and JSON

---

## 3. Key Features & Algorithms

### Hard Constraints (Must be satisfied)
✓ No instructor teaches two courses simultaneously
✓ No room is double-booked
✓ No student section has schedule conflicts
✓ Instructors only teach courses they are qualified for
✓ Rooms accommodate section size (capacity ≥ student count)
✓ Consecutive time slots exist for multi-slot sessions

### Soft Constraints (Minimized)
→ Prefer instructors' available time slots
→ Minimize schedule gaps in instructor calendars
→ Avoid very early morning classes
→ Keep multi-slot sessions in consecutive slots

### Algorithms Implemented

**Phase 1: Backtracking with Constraint Checking**
- Variable selection: Most Constrained Variable (smallest domain first)
- Value selection: Least Constraining Value (minimizes domain pruning)
- Forward checking: Eliminates inconsistent values from future domains
- Consistency checks: Validates instructor, room, and section schedules

**Phase 2: Iterative Local Search**
- Start with Phase 1 solution (local minimum)
- Random assignment swaps within iterations
- Accept all cost-reducing moves
- Configurable iteration count for solution refinement

---

## 4. File Structure & Organization

```
timetable_scheduler/
├── main.py                    # Entry point, orchestrates pipeline
├── requirements.txt           # Python dependencies (pandas, openpyxl)
├── README.md                  # User documentation
├── PROJECT_REPORT.md          # This file
│
├── Data/                      # Input and output data
│   ├── Courses.csv
│   ├── Instructors.csv
│   ├── Rooms.csv
│   ├── TimeSlots.csv
│   ├── sections_data.xlsx
│   ├── Avilable_Course.csv
│   ├── final_timetable.csv    # Generated output
│   └── timetable_data.json
│
├── data_loader/               # Data input pipeline
│   ├── __init__.py
│   └── loader.py              # DataLoader class
│
├── models/                    # Domain models
│   ├── __init__.py
│   ├── entities.py            # Course, Instructor, Room, TimeSlot, Section
│   └── session.py             # Session, VariableGenerator
│
├── csp/                       # Constraint satisfaction solver
│   ├── __init__.py
│   ├── domain.py              # DomainBuilder class
│   ├── solver_phase1.py       # BacktrackingSolver
│   ├── solver_phase2.py       # CostEvaluator, IterativeSolver
│   └── utils.py               # Helper utilities
│
└── output/                    # Result export
    ├── __init__.py
    └── export.py              # save_solution_to_csv, save_solution_to_json
```

---

## 5. Usage Guide

### Prerequisites
```bash
pip install -r requirements.txt
```

### Input Data Preparation

Place the following CSV/XLSX files in the `Data/` directory:

1. **Courses.csv**
   - Columns: course_id, name, lecture_duration, lab_duration, lab_type
   - Example: `CS101,Python Basics,2,2,programming`

2. **Instructors.csv**
   - Columns: instructor_id, name, qualified_courses, not_preferred_slots
   - Example: `I001,Dr. Smith,"CS101,CS102",5,6,7`

3. **Rooms.csv**
   - Columns: room_id, capacity, room_type, type_of_space
   - Example: `R101,50,lecture,classroom`

4. **TimeSlots.csv**
   - Columns: slot_id, day, start_time, end_time
   - Example: `1,Monday,08:00,10:00`

5. **sections_data.xlsx**
   - Columns: section_id, department, level, specialization, student_count

6. **Avilable_Course.csv**
   - Maps department-level-specialization to courses with preferences

### Running the Scheduler

```bash
python main.py
```

**Output**:
- `Data/final_timetable.csv` - Timetable in CSV format
- `Data/timetable_data.json` - Timetable in JSON format

### Configuration

Edit [main.py](main.py) to modify:
- Input file paths (FILE_PATHS dictionary)
- Output file names (OUTPUT_FILE, OUTPUT_JSON_FILE)
- Group capacity (VariableGenerator max_group_capacity parameter)
- Optimization iterations (IterativeSolver iterations parameter)

---

## 6. Performance Characteristics

### Time Complexity
- **Phase 1**: O(b^d) worst case (exponential), where b = branching factor, d = depth
  - Mitigated by constraint propagation and heuristics
- **Phase 2**: O(I × M) where I = iterations, M = moves per iteration
  - Configurable for speed-quality tradeoff

### Space Complexity
- O(V × D) where V = variables, D = average domain size
- Manageable for typical university scheduling problems (100-500 courses)

### Scalability Considerations
- **Small institutions** (50-100 courses): Solves in seconds
- **Medium institutions** (200-500 courses): Solves in minutes
- **Large institutions** (1000+ courses): May require constraint adjustment or problem decomposition

---

## 7. Strengths & Advantages

✅ **Automated Solution**: Eliminates manual timetable creation effort
✅ **Constraint Flexibility**: Easily configurable soft constraints
✅ **Quality Optimization**: Two-phase approach balances feasibility and optimality
✅ **Clear Architecture**: Well-organized, extensible codebase
✅ **Multiple Output Formats**: CSV and JSON exports for different use cases
✅ **Detailed Modeling**: Accounts for lecture/lab splits and group capacity
✅ **Preference Satisfaction**: Optimizes instructor and room preferences

---

## 8. Limitations & Future Improvements

### Current Limitations
- ❌ No GUI/web interface (CLI only)
- ❌ Limited to single institution at a time
- ❌ No interactive conflict resolution
- ❌ No comprehensive error handling/validation messaging
- ❌ No progress reporting during long solves
- ❌ Limited to CSV/JSON output formats

### Recommended Enhancements

**Short Term**:
1. Add input validation and error reporting
2. Implement progress indicators during solving
3. Add constraint violation reporting for unsolvable problems
4. Create REST API for scheduling service

**Medium Term**:
1. Develop web UI for managing inputs and viewing results
2. Add support for cross-institution scheduling
3. Implement constraint templates (e.g., "no Monday-Wednesday gaps")
4. Add scheduling history and version management
5. Optimize solver performance for large-scale problems

**Long Term**:
1. Machine learning for constraint learning from historical schedules
2. Multi-objective optimization (balance multiple goals)
3. Real-time rescheduling with minimal disruption
4. Integration with student information systems (SIS)
5. Parallel solving for multiple departments

---

## 9. Technical Specifications

### Dependencies
- **pandas**: Data manipulation and CSV/Excel I/O
- **openpyxl**: Excel file format support

### Language & Version
- **Python 3.7+** (recommended: 3.9+)
- No external constraint solver libraries (pure Python implementation)

### Platform Support
- Linux, macOS, Windows
- No platform-specific dependencies

### Code Style
- Clean, documented codebase
- Dataclasses for data models
- Type hints recommended for future versions

---

## 10. Testing & Validation

### Test Coverage
- [test.py](test.py) - Contains project test cases
- Test scenarios include:
  - Data loading validation
  - Variable generation accuracy
  - Domain construction correctness
  - Phase 1 feasibility verification
  - Phase 2 cost calculation validation

### Validation Steps
1. Verify no schedule conflicts exist
2. Confirm instructor qualifications
3. Check room capacity sufficiency
4. Validate consecutive slot assignments
5. Monitor cost reduction across solver phases

---

## 11. Conclusion

The **Timetable Scheduler** is a robust, well-architected solution to the university course timetabling problem. By combining constraint satisfaction techniques with local search optimization, it produces high-quality timetables that satisfy institutional constraints while minimizing soft constraint violations.

The two-phase approach ensures both **feasibility** (Phase 1) and **quality** (Phase 2), and the modular design facilitates future enhancements and integrations. This system can significantly reduce the administrative burden of timetable creation while improving schedule quality and instructor satisfaction.

### Recommended Next Steps
1. Deploy to production environment with real institutional data
2. Implement API layer for integration with SIS
3. Develop web-based scheduling interface
4. Establish performance baselines with various problem sizes
5. Gather stakeholder feedback for constraint refinements

---

**Report Generated**: December 15, 2025
**Project Status**: Production-ready with opportunities for enhancement
