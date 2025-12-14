# ===============================
# solver_phase2.py
# Phase 2: Local Search Optimization
# ===============================

import random
import time
import copy
from csp.solver_phase1 import Assignment


class CostEvaluator:
    """Calculates the total penalty ('cost') of a complete solution."""

    def __init__(self, model_data):
        self.model_data = model_data
        # Pre-build day-to-slots map for gap calculation
        self.slots_by_day = {}
        for slot in model_data['timeslots'].values():
            if slot.day not in self.slots_by_day:
                self.slots_by_day[slot.day] = []
            self.slots_by_day[slot.day].append(slot.slot_id)
        for day in self.slots_by_day:
            self.slots_by_day[day].sort()

    def calculate_total_cost(self, solution, state):
        total_penalty = 0

        # 1. Instructor Preference Penalties
        for assignment in solution:
            inst = assignment.instructor
            # A. Not Preferred Slot
            for slot_id in assignment.timeslot_sequence:
                if slot_id in inst.not_preferred_slots:
                    total_penalty += 10

            # B. Not Preferred Instructor
            session = assignment.session
            if session.preferred_instructors and inst.instructor_id not in session.preferred_instructors:
                total_penalty += 5

        # 2. Student Gap Penalties
        # This is the most complex one
        for section in self.model_data['sections'].values():
            total_penalty += self._calculate_gaps_for_section(section.section_id, state)

        return total_penalty

    def _calculate_gaps_for_section(self, section_id, state):
        """Calculates gap penalties for a single section."""
        gap_penalty = 0
        busy_slots = state.section_schedule[section_id]
        if not busy_slots:
            return 0

        for day, slot_ids_in_day in self.slots_by_day.items():
            # Get the slots this section is busy *on this day*
            day_busy_slots = [s for s in slot_ids_in_day if s in busy_slots]
            day_busy_slots.sort()

            # Find gaps between consecutive sessions
            for i in range(len(day_busy_slots) - 1):
                slot_after = day_busy_slots[i+1]
                slot_before = day_busy_slots[i]

                # We need to find the "end" slot of the first session
                # This is a simplification: assumes 1-slot duration
                # A full solution would track end-times.
                # For now, we just count gaps between start slots.

                gap_size = slot_after - slot_before

                if gap_size == 2:  # e.g., busy at slot 1, then slot 3. Gap is 1 slot.
                    gap_penalty += 1
                elif gap_size == 3:  # e.g., busy at 1, then 4. Gap is 2 slots.
                    gap_penalty += 3  # Heavier penalty for larger gap
                elif gap_size > 3:
                    gap_penalty += 5
        return gap_penalty


class IterativeSolver:
    """
    Phase 2: Takes a valid solution and tries to improve it
    using a simple hill-climbing metaheuristic.
    """
    def __init__(self, solution, state, evaluator, model_data, iterations=10000):
        self.current_solution = solution  # List of Assignments
        self.current_state = state  # TimetableState object
        self.evaluator = evaluator
        self.model_data = model_data
        self.iterations = iterations
        self.current_cost = evaluator.calculate_total_cost(solution, state)

    def optimize(self):
        print(f"\n--- Phase 2: Iterative Optimizer Starting ---")
        print(f"Initial Cost: {self.current_cost}")
        start_time = time.time()

        for i in range(self.iterations):
            if i % 2000 == 0:
                print(f"Iteration {i}...")

            # 1. Generate a "neighbor" solution
            # A neighbor is a solution with one small, valid change.
            neighbor_solution, neighbor_state = self.generate_neighbor()
            if neighbor_solution is None:
                continue  # Could not find a valid swap

            # 2. Evaluate the neighbor
            new_cost = self.evaluator.calculate_total_cost(neighbor_solution, neighbor_state)

            # 3. Decide to accept
            # This is simple Hill Climbing: only accept better solutions
            if new_cost < self.current_cost:
                self.current_solution = neighbor_solution
                self.current_state = neighbor_state
                self.current_cost = new_cost
                print(f"  > Improvement found! New Cost: {new_cost} (Iteration {i})")

        end_time = time.time()
        print(f"--- Optimizer Finished in {end_time - start_time:.2f} seconds ---")
        print(f"Final Optimized Cost: {self.current_cost}")
        return self.current_solution

    def generate_neighbor(self):
        """Tries to make one valid swap."""

        # Pick two random assignments to try and swap
        if len(self.current_solution) < 2:
            return None, None

        a1, a2 = random.sample(self.current_solution, 2)

        # We can only swap if they have the same duration
        if a1.session.duration_slots != a2.session.duration_slots:
            return None, None

        # Create copies to work with
        neighbor_state = copy.deepcopy(self.current_state)
        neighbor_solution = list(self.current_solution)  # Shallow copy of list

        # --- The Swap ---
        # 1. Remove both from state
        neighbor_state.remove_assignment(a1)
        neighbor_state.remove_assignment(a2)

        # 2. Create the two "swapped" potential assignments
        new_a1 = Assignment(a1.session, a2.timeslot_sequence, a2.room, a2.instructor)
        new_a2 = Assignment(a2.session, a1.timeslot_sequence, a1.room, a1.instructor)

        # 3. Check if the swap is valid (respects hard constraints)
        # This is complex: new_a1 must be valid for session 1, and new_a2 for session 2.

        # Check if new_a1 is valid for session a1
        valid_a1 = (new_a1.instructor in a1.session.domain.instructors and
                    new_a1.room in a1.session.domain.rooms and
                    new_a1.timeslot_sequence in a1.session.domain.timeslot_sequences and
                    neighbor_state.is_consistent(new_a1.session, new_a1.timeslot_sequence, new_a1.room, new_a1.instructor))

        if not valid_a1:
            return None, None  # Swap failed

        # Add new_a1 to the state so we can check new_a2 against it
        neighbor_state.add_assignment(new_a1)

        # Check if new_a2 is valid for session a2
        valid_a2 = (new_a2.instructor in a2.session.domain.instructors and
                    new_a2.room in a2.session.domain.rooms and
                    new_a2.timeslot_sequence in a2.session.domain.timeslot_sequences and
                    neighbor_state.is_consistent(new_a2.session, new_a2.timeslot_sequence, new_a2.room, new_a2.instructor))

        if not valid_a2:
            return None, None  # Swap failed

        # 4. If both are valid, finalize the neighbor
        neighbor_state.add_assignment(new_a2)

        # Update the neighbor solution list
        neighbor_solution.remove(a1)
        neighbor_solution.remove(a2)
        neighbor_solution.append(new_a1)
        neighbor_solution.append(new_a2)

        return neighbor_solution, neighbor_state
