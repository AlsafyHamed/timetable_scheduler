# ===============================
# solver_phase2.py
# Phase 2: Local Search Optimization
# ===============================

import random
import time
import copy


class CostEvaluator:
    """Evaluates quality of a given timetable solution."""

    def __init__(self, model_data):
        self.model_data = model_data

    def calculate_cost(self, solution):
        """Assigns a cost score (lower = better)."""
        penalty = 0

        # Penalize late-day sessions or instructor conflicts
        for assignment in solution:
            session = assignment.session
            timeslot_seq = assignment.timeslot_sequence
            instructor = assignment.instructor

            # Instructor not preferred slot penalty
            for slot in timeslot_seq:
                if slot in instructor.not_preferred_slots:
                    penalty += 3

            # Small room capacity penalty
            if assignment.room.capacity < session.total_student_count:
                penalty += 5

            # Prefer spreading sessions across days
            if session.course.lab_type == "lab" and len(timeslot_seq) > 1:
                penalty += 1

        return penalty


class IterativeSolver:
    """Performs local search optimization (hill climbing style)."""

    def __init__(self, initial_solution, initial_state, evaluator, model_data, iterations=10000):
        self.current_solution = copy.deepcopy(initial_solution)
        self.current_state = initial_state
        self.evaluator = evaluator
        self.model_data = model_data
        self.iterations = iterations
        self.best_solution = copy.deepcopy(initial_solution)
        self.best_cost = evaluator.calculate_cost(initial_solution)

    def optimize(self):
        print("\n[Phase 2] Starting Iterative Optimization...")

        start_time = time.time()

        for i in range(self.iterations):
            new_solution = self._generate_neighbor(self.current_solution)
            new_cost = self.evaluator.calculate_cost(new_solution)

            if new_cost < self.best_cost:
                self.best_cost = new_cost
                self.best_solution = copy.deepcopy(new_solution)
                self.current_solution = new_solution

            # Occasionally accept worse solutions to escape local minima
            elif random.random() < 0.01:
                self.current_solution = new_solution

            if i % 1000 == 0:
                print(f"  Iter {i:5d} | Best cost: {self.best_cost}")

        duration = time.time() - start_time
        print(f"[Phase 2] Optimization completed in {duration:.2f}s | Best cost = {self.best_cost} ✅")

        return self.best_solution

    def _generate_neighbor(self, solution):
        """Randomly modifies one assignment to explore neighborhood."""
        neighbor = copy.deepcopy(solution)

        if not neighbor:
            return solution

        idx = random.randint(0, len(neighbor) - 1)
        assignment = neighbor[idx]
        domain = assignment.session.domain

        # Randomly tweak one of (room, instructor, timeslot)
        choice = random.choice(["room", "instructor", "timeslot"])

        if choice == "room" and domain.rooms:
            assignment.room = random.choice(domain.rooms)
        elif choice == "instructor" and domain.instructors:
            assignment.instructor = random.choice(domain.instructors)
        elif choice == "timeslot" and domain.timeslot_sequences:
            assignment.timeslot_sequence = random.choice(domain.timeslot_sequences)

        neighbor[idx] = assignment
        return neighbor
