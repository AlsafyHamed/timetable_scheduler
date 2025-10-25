# Timetable Scheduler

A small Python project that builds timetables using constraint satisfaction techniques.

## Overview

This project implements a timetable scheduler that assigns courses, instructors, rooms, and time slots using a two-phase solver:
- Phase 1: Backtracking CSP to find a feasible schedule.
- Phase 2: Local search to improve solution quality.

It reads input CSV/XLSX files from the `data/` folder and produces a final timetable CSV.

## Quick start

1. Install dependencies:
```sh
pip install -r requirements.txt
```

2. Ensure input files are present in `data/`:
- Courses.csv, Instructors.csv, Rooms.csv, TimeSlots.csv, sections_data.xlsx, Avilable_Course.csv

3. Run the scheduler:
```sh
python main.py
```

By default the app writes output to `final_timetable.csv` as configured in [main.py](main.py).

## Project structure

- [main.py](main.py) — entry point that wires components and runs both solver phases.
- data_loader/loader.py — loads CSV/XLSX into model objects.
- models/
  - [models/session.py](models/session.py) — session model and variable generator (see [`models.session.VariableGenerator`](models/session.py)).
  - [models/entities.py](models/entities.py) — domain entities (Course, Room, Instructor, TimeSlot, Section).
- csp/
  - [csp/domain.py](csp/domain.py) — domain generation and [`csp.domain.DomainBuilder`](csp/domain.py).
  - [csp/solver_phase1.py](csp/solver_phase1.py) — backtracking solver and [`csp.solver_phase1.BacktrackingSolver`](csp/solver_phase1.py).
  - [csp/solver_phase2.py](csp/solver_phase2.py) — cost evaluation and local search optimizer.
- output/
  - [output/export.py](output/export.py) — CSV export helper (see [`output.export.save_solution_to_csv`](output/export.py)).

## Notes

- Large CSVs may be tracked with Git LFS. See `.gitattributes`.
- If input data changes, re-run `python main.py` to regenerate timetable.
- The code is structured for clarity and ease of extension; adjust constraints or evaluator heuristics in `csp/` as needed.

## Contributing

1. Fork the repo
2. Create a feature branch
3. Add tests where appropriate
4. Open a PR with a clear description

## License

Add a LICENSE file if you want to choose a license (MIT recommended).

<!-- end of file -->
