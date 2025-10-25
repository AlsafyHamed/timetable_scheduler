# ===============================
# solver_phase1.py
# Phase 1: Backtracking CSP Solver
# ===============================

from dataclasses import dataclass
import time


@dataclass
class Assignment:
    """Represents a single assignment of a session."""
    session: object
    timeslot_sequence: list
    room: object
    instructor: object


class TimetableState:
    """Tracks current timetable assignments and ensures constraints."""

    def __init__(self):
        self.assignments = []
        self.instructor_usage = {}
        self.room_usage = {}
        self.section_usage = {}

    def is_consistent(self, session, timeslot_seq, room, instructor):
        """Check for constraint conflicts before assignment."""

        # Instructor conflict
        for slot in timeslot_seq:
            if (instructor.instructor_id, slot) in self.instructor_usage:
                return False

        # Room conflict
        for slot in timeslot_seq:
            if (room.room_id, slot) in self.room_usage:
                return False

        # Section conflict
        for section in session.sections:
            for slot in timeslot_seq:
                if (section.section_id, slot) in self.section_usage:
                    return False

        return True

    def add_assignment(self, session, timeslot_seq, room, instructor):
        """Add a valid assignment to state."""
        assignment = Assignment(session, timeslot_seq, room, instructor)
        self.assignments.append(assignment)

        for slot in timeslot_seq:
            self.instructor_usage[(instructor.instructor_id, slot)] = True
            self.room_usage[(room.room_id, slot)] = True
            for section in session.sections:
                self.section_usage[(section.section_id, slot)] = True

    def remove_assignment(self, session, timeslot_seq, room, instructor):
        """Undo assignment (for backtracking)."""
        self.assignments = [a for a in self.assignments if a.session != session]

        for slot in timeslot_seq:
            self.instructor_usage.pop((instructor.instructor_id, slot), None)
            self.room_usage.pop((room.room_id, slot), None)
            for section in session.sections:
                self.section_usage.pop((section.section_id, slot), None)


class BacktrackingSolver:
    """Backtracking CSP Solver to find a feasible initial timetable."""

    def __init__(self, variables, model_data):
        self.variables = variables
        self.model_data = model_data
        self.best_solution = None
        self.best_state = None
        self.start_time = None

    def solve(self):
        print("\n[Phase 1] Starting Backtracking Search...")
        self.start_time = time.time()
        state = TimetableState()
        success = self._backtrack(state, 0)
        duration = time.time() - self.start_time

        if success:
            print(f"[Phase 1] Solution found in {duration:.2f} seconds ✅")
            return self.best_solution, self.best_state
        else:
            print(f"[Phase 1] No valid timetable found after {duration:.2f} seconds ❌")
            return None, None

    def _backtrack(self, state, index):
        """Recursive backtracking search with constraint checking."""
        if index == len(self.variables):
            self.best_solution = list(state.assignments)
            self.best_state = state
            return True

        session = self.variables[index]
        domain = session.domain

        # Try each possible combination in domain
        for instructor in domain.instructors:
            for room in domain.rooms:
                for timeslot_seq in domain.timeslot_sequences:
                    if state.is_consistent(session, timeslot_seq, room, instructor):
                        state.add_assignment(session, timeslot_seq, room, instructor)

                        if self._backtrack(state, index + 1):
                            return True

                        # Backtrack
                        state.remove_assignment(session, timeslot_seq, room, instructor)

        return False
