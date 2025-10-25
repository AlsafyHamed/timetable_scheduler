# Timetable Scheduler

A small Python project that builds timetables using constraint satisfaction techniques.

## Overview

This project implements a timetable scheduler that assigns courses, instructors, rooms, and time slots using constraint solving (CSP) across two solver phases. It reads input CSVs from the `data/` folder and produces a final timetable CSV.

Key features:
- Constraint-based scheduling (CSP)
- Two-phase solver (phase1/phase2) to improve solution quality
- Data-driven: CSV inputs for courses, instructors, rooms, and timeslots

## Repository structure

- `main.py` - entry point to run the scheduler
- `requirements.txt` - Python dependencies
- `csp/` - implementation of CSP domain, solvers, and utilities
  - `domain.py`, `solver_phase1.py`, `solver_phase2.py`, `utils.py`
- `data/` - input CSVs (Courses, Instructors, Rooms, TimeSlots, etc.)
- `data_loader/` - code that loads CSVs into the app
- `models/` - entities, session and data models
- `output/` - export functionality for final timetables

## Requirements

- Python 3.8+ (recommended)
- Install dependencies:

```powershell
pip install -r requirements.txt
```

## How to run

1. Prepare your input CSV files in the `data/` directory. Example files are already present (Courses.csv, Instructors.csv, Rooms.csv, TimeSlots.csv).
2. Run the scheduler:

```powershell
cd D:\projects\timetable_scheduler
python main.py
```

The program writes output to `data/final_timetable.csv` (or the configured output location).

## Notes on data files

- Large CSVs may be tracked via Git LFS in this repository. If you prefer not to store large datasets in the repository, add `data/` to `.gitignore` and provide instructions to obtain datasets separately.

## Contributing

Feel free to open issues or pull requests. For changes to code, add tests where appropriate and follow standard Python packaging/style.

## License

This repository does not include a license file yet. If you want a permissive license, consider adding an `LICENSE` with the MIT license.

---
Generated README for the timetable scheduler project.
