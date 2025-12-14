# ===============================
# solver_phase1.py
# Phase 1: Backtracking CSP Solver
# ===============================

from dataclasses import dataclass
import time


@dataclass
class Assignment:
    session: object
    timeslot_sequence: list
    room: object
    instructor: object

    def __repr__(self):
        return (f"Assignment(Session={self.session.session_id}, "
                f"Course={self.session.course.course_id}, "
                f"Time={self.timeslot_sequence}, Room={self.room.room_id}, "
                f"Inst={self.instructor.instructor_id})")


class TimetableState:
    def __init__(self, model_data):
        self.instructor_schedule = {inst.instructor_id: set() for inst in model_data['instructors'].values()}
        self.room_schedule = {room.room_id: set() for room in model_data['rooms'].values()}
        self.section_schedule = {sec.section_id: set() for sec in model_data['sections'].values()}

    def is_consistent(self, session, timeslot_sequence, room, instructor):
        try:
            for slot_id in timeslot_sequence:
                if (slot_id in self.instructor_schedule[instructor.instructor_id] or
                    slot_id in self.room_schedule[room.room_id]):
                    return False
                for section in session.sections:
                    if slot_id in self.section_schedule[section.section_id]:
                        return False
            return True
        except KeyError as e:
            print(f"--- CRITICAL ERROR in TimetableState.is_consistent: {e} ---")
            return False

    def add_assignment(self, assignment):
        for slot_id in assignment.timeslot_sequence:
            self.instructor_schedule[assignment.instructor.instructor_id].add(slot_id)
            self.room_schedule[assignment.room.room_id].add(slot_id)
            for section in assignment.session.sections:
                self.section_schedule[section.section_id].add(slot_id)

    def remove_assignment(self, assignment):
        for slot_id in assignment.timeslot_sequence:
            self.instructor_schedule[assignment.instructor.instructor_id].remove(slot_id)
            self.room_schedule[assignment.room.room_id].remove(slot_id)
            for section in assignment.session.sections:
                self.section_schedule[section.section_id].remove(slot_id)


class BacktrackingSolver:
    def __init__(self, variables, model_data):
        self.unassigned_variables = list(variables)
        self.state = TimetableState(model_data)
        self.solution = []
        self.model_data = model_data  # Save for LCV

    def solve(self):
        print("\n--- Phase 1: Backtracking Solver Starting ---")
        start_time = time.time()

        self.unassigned_variables.sort(key=self.get_domain_size)

        solution_found = self.recursive_solve()

        end_time = time.time()
        print(f"--- Solver Finished in {end_time - start_time:.2f} seconds ---")

        if solution_found:
            print(f"SUCCESS: Found a valid timetable with {len(self.solution)} assignments.")
            # We also need to return the final state for Phase 2
            return self.solution, self.state
        else:
            print("FAILURE: Could not find a valid solution.")
            return None, None

    def get_domain_size(self, var):
        d = var.domain
        return len(d.timeslot_sequences) * len(d.rooms) * len(d.instructors)

    def select_variable_mrv(self):
        # A more dynamic MRV: re-sort the list and pick the best one
        # This is slower but more accurate
        self.unassigned_variables.sort(key=self.get_domain_size)
        return self.unassigned_variables.pop(0)

    def get_ordered_domain_values(self, var):
        """
        Generates all (time, room, inst) combinations.
        We will now also sort them based on our LCV / Soft Constraints!
        """
        all_combinations = []
        for time_seq in var.domain.timeslot_sequences:
            for room in var.domain.rooms:
                for inst in var.domain.instructors:
                    all_combinations.append((time_seq, room, inst))

        # --- LCV / Soft Constraint Heuristic ---
        # We calculate a "penalty" for each choice.
        # Choices with LOWER penalty are tried FIRST.
        def calculate_penalty(value_tuple):
            time_seq, room, inst = value_tuple
            penalty = 0

            # 1. Penalty for Not Preferred Slot
            for slot_id in time_seq:
                if slot_id in inst.not_preferred_slots:
                    penalty += 10  # High penalty

            # 2. Penalty for Not Preferred Instructor
            if inst.instructor_id not in var.preferred_instructors and var.preferred_instructors:
                penalty += 5  # Medium penalty

            # 3. Reward for Preferred Instructor (negative penalty)
            if inst.instructor_id in var.preferred_instructors:
                penalty -= 20  # Strong reward

            return penalty

        # Sort combinations: lowest penalty score first
        all_combinations.sort(key=calculate_penalty)
        return all_combinations

    def recursive_solve(self):
        if not self.unassigned_variables:
            return True

        # Use simple pop(0) after initial sort for speed
        var = self.unassigned_variables.pop(0)

        for time_seq, room, inst in self.get_ordered_domain_values(var):
            if self.state.is_consistent(var, time_seq, room, inst):
                assignment = Assignment(var, time_seq, room, inst)
                self.state.add_assignment(assignment)
                self.solution.append(assignment)

                if self.recursive_solve():
                    return True

                self.solution.pop()
                self.state.remove_assignment(assignment)

        self.unassigned_variables.insert(0, var)
        return False
