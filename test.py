import pandas as pd
import ast
import math
import time
import random
from dataclasses import dataclass
import copy # Needed for Phase 2 to deepcopy solutions

print("--- Loading Part 1: Data Loader (Prerequisite) ---")

FILE_PATHS = {
    "courses": "/content/Courses.csv",
    "rooms": "/content/Rooms.csv",
    "instructors": "/content/Instructors.csv",
    "timeslots": "/content/TimeSlots.csv",
    "sections": "/content/sections_data.xlsx",
    "available_courses": "/content/Avilable_Course.csv"
}
OUTPUT_FILE = "final_timetable.csv"
class Course:
    def __init__(self, course_id, name, lecture_duration, lab_duration, lab_type):
        self.course_id = course_id
        self.name = name
        self.lecture_duration = int(lecture_duration)
        self.lab_duration = int(lab_duration)
        self.lab_type = lab_type
    def __repr__(self):
        return f"Course(id={self.course_id}, name={self.name})"

class Room:
    def __init__(self, room_id, capacity, room_type, type_of_space):
        self.room_id = room_id
        self.capacity = int(capacity)
        self.room_type = room_type
        self.type_of_space = type_of_space
    def __repr__(self):
        return f"Room(id={self.room_id}, capacity={self.capacity}, type={self.type_of_space})"

class Instructor:
    def __init__(self, instructor_id, name, qualified_courses_set, not_preferred_slots_set):
        self.instructor_id = instructor_id
        self.name = name
        self.qualified_courses = qualified_courses_set
        self.not_preferred_slots = not_preferred_slots_set
    def __repr__(self):
        return f"Instructor(id={self.instructor_id}, name={self.name})"

class TimeSlot:
    def __init__(self, slot_id, day, start_time, end_time):
        self.slot_id = int(slot_id)
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
    def __repr__(self):
        return f"TimeSlot(id={self.slot_id}, day={self.day}, time={self.start_time})"

class Section:
    def __init__(self, section_id, department, level, specialization, student_count):
        self.section_id = section_id
        self.department = department
        self.level = int(level)
        self.specialization = specialization
        self.student_count = int(student_count)
    def __repr__(self):
        return f"Section(id={self.section_id}, level={self.level}, count={self.student_count})"

class AvailableCourse:
    def __init__(self, department, level, specialization, course_id, preferred_prof, preferred_assi_set):
        self.department = department
        self.level = int(level)
        self.specialization = specialization
        self.course_id = course_id
        self.preferred_prof = preferred_prof
        self.preferred_assi = preferred_assi_set
    def __repr__(self):
        return f"Available(level={self.level}, course={self.course_id}, prof={self.preferred_prof})"

# --- 3. DATA LOADER CLASS (Copied, with all fixes) ---

class DataLoader:
    def __init__(self, paths):
        self.paths = paths
        self.model_data = {}

    def load_all(self):
        print("Loading all data sources...")
        try:
            self.model_data['courses'] = self._load_courses()
            self.model_data['rooms'] = self._load_rooms()
            self.model_data['instructors'] = self._load_instructors()
            slots_dict, slots_df = self._load_timeslots()
            self.model_data['timeslots'] = slots_dict
            self.model_data['timeslots_df'] = slots_df
            self.model_data['sections'] = self._load_sections()
            self.model_data['available_courses'] = self._load_available_courses()
            print("All data loaded and model objects created.")
            return self.model_data
        except Exception as e:
            print(f"Error during data loading: {e}")
            return None

    def _load_courses(self):
        df = pd.read_csv(self.paths['courses'])
        courses_dict = {}
        for row in df.to_dict('records'):
            course_id_clean = str(row['CourseID']).strip()
            course = Course(course_id_clean, row['CourseName'], row['Lecture'], row['Lab'], row['Lab_Type'])
            courses_dict[course.course_id] = course
        return courses_dict

    def _load_rooms(self):
        df = pd.read_csv(self.paths['rooms'])
        return {row['RoomID']: Room(row['RoomID'], row['Capacity'], row['Type'], row['Type_of_Space']) for row in df.to_dict('records')}

    def _load_instructors(self):
        df = pd.read_csv(self.paths['instructors'])
        instructors_dict = {}
        for row in df.to_dict('records'):
            qualified = set(c.strip() for c in str(row['QualifiedCourses']).split(','))
            not_preferred = set()
            try:
                not_preferred_list = ast.literal_eval(row['Not_PreferredSlots'])
                if isinstance(not_preferred_list, list): not_preferred = set(not_preferred_list)
            except Exception: pass
            instructors_dict[row['InstructorID']] = Instructor(row['InstructorID'], row['Name'], qualified, not_preferred)
        return instructors_dict

    def _load_timeslots(self):
        df = pd.read_csv(self.paths['timeslots'])
        df = df.sort_values(by='ID').reset_index(drop=True)
        timeslots_dict = {row['ID']: TimeSlot(row['ID'], row['Day'], row['StartTime'], row['EndTime']) for row in df.to_dict('records')}
        return timeslots_dict, df

    def _load_sections(self):
        df = pd.read_excel(self.paths['sections'])
        return {row['SectionID']: Section(row['SectionID'], row['Department'], row['Level'], row['Specialization'], row['StudentCount']) for row in df.to_dict('records')}

    def _load_available_courses(self):
        df = pd.read_csv(self.paths['available_courses'])
        available_list = []
        for row in df.to_dict('records'):
            prof = row['preferred_Prof'] if pd.notna(row['preferred_Prof']) else None
            assi_set = set()
            assi_str = str(row['preferred_Assi'])
            if pd.notna(assi_str) and assi_str.lower() != 'nan':
                 assi_set = set(c.strip() for c in assi_str.split(','))
            course_id_clean = str(row['CourseID']).strip()
            available_list.append(AvailableCourse(row['Department'], row['Level'], row['Specialization'], course_id_clean, prof, assi_set))
        return available_list

print("--- End of Prerequisite Code (Part 1) ---")

# --- ************************************** ---
# --- STEP 2: CSP VARIABLE (ClassSession)    ---
# --- (Copied)                             ---
# --- ************************************** ---

class ClassSession:
    _session_counter = 0
    def __init__(self, course, session_type, duration_slots):
        ClassSession._session_counter += 1
        self.session_id = f"S{ClassSession._session_counter}"
        self.course, self.session_type, self.duration_slots = course, session_type, duration_slots
        self.sections, self.preferred_instructors = [], set()
        self.total_student_count, self.is_small_group = 0, False
        self.domain = None
    def add_section(self, section):
        if section not in self.sections:
            self.sections.append(section)
            self.total_student_count += section.student_count
    def set_small_group_flag(self, max_capacity):
        self.is_small_group = (self.total_student_count < max_capacity)
    def get_group_name(self):
        return self.sections[0].section_id if self.session_type == 'Lab' else f"Group ({','.join([s.section_id for s in self.sections])})"
    def __repr__(self):
        return f"ClassSession(id={self.session_id}, desc='{self.session_type[:3].upper()}-{self.course.course_id}', students={self.total_student_count})"

class VariableGenerator:
    def __init__(self, model_data, max_group_capacity=75):
        self.model_data, self.max_capacity = model_data, max_group_capacity
        self.all_variables = []
    def generate_all_variables(self):
        print(f"\n--- Starting Variable Generation (Max Capacity={self.max_capacity}) ---")
        ClassSession._session_counter = 0
        for req in self.model_data['available_courses']:
            try:
                course_obj = self.model_data['courses'][req.course_id]
            except KeyError: continue
            matching_sections = [sec for sec in self.model_data['sections'].values() if
                                 (sec.department == req.department and sec.level == req.level and
                                  (req.specialization == 'Core' or req.specialization == sec.specialization))]
            if not matching_sections: continue
            if course_obj.lecture_duration > 0: self._create_lecture_variables(course_obj, matching_sections, req)
            if course_obj.lab_duration > 0: self._create_lab_variables(course_obj, matching_sections, req)
        print(f"--- Variable Generation Complete: {len(self.all_variables)} total sessions. ---")
        return self.all_variables
    def _create_lecture_variables(self, course_obj, sections, request):
        sections_sorted = sorted(sections, key=lambda s: s.section_id)
        current_group = None
        for section in sections_sorted:
            if current_group is None or (current_group.total_student_count + section.student_count) > self.max_capacity:
                if current_group:
                    current_group.set_small_group_flag(self.max_capacity)
                    self.all_variables.append(current_group)
                current_group = ClassSession(course_obj, 'Lecture', course_obj.lecture_duration)
                if request.preferred_prof: current_group.preferred_instructors.add(request.preferred_prof)
            current_group.add_section(section)
        if current_group:
            current_group.set_small_group_flag(self.max_capacity)
            self.all_variables.append(current_group)
    def _create_lab_variables(self, course_obj, sections, request):
        for section in sections:
            lab_session = ClassSession(course_obj, 'Lab', course_obj.lab_duration)
            lab_session.add_section(section)
            lab_session.set_small_group_flag(self.max_capacity)
            lab_session.preferred_instructors = request.preferred_assi
            self.all_variables.append(lab_session)

print("--- End of Prerequisite Code (Part 2) ---")

# --- ************************************** ---
# --- STEP 3: CSP DOMAIN (Copied)            ---
# --- ************************************** ---

class Domain:
    def __init__(self, session_variable, model_data):
        self.variable = session_variable
        self.timeslot_sequences = self._generate_consecutive_sequences(
            model_data['timeslots_df'], session_variable.duration_slots)
        self.rooms = self._filter_rooms(
            session_variable, model_data['rooms'])
        self.instructors = self._filter_instructors(
            session_variable, model_data['instructors'])
    def _generate_consecutive_sequences(self, all_timeslots_df, duration):
        sequences, day_slots = [], {}
        for row in all_timeslots_df.sort_values(by='ID').to_dict('records'):
            day = row['Day']
            if day not in day_slots: day_slots[day] = []
            day_slots[day].append(row['ID'])
        for day in day_slots:
            slots = day_slots[day]
            for i in range(len(slots) - duration + 1):
                sequence = slots[i : i + duration]
                if all(sequence[j+1] == sequence[j] + 1 for j in range(len(sequence) - 1)):
                    sequences.append(sequence)
        return sequences
    def _filter_rooms(self, session, all_rooms):
        valid_rooms, EXCLUDED_LECTURE_SPACES = [], {'Drawing Studio', 'Computer'}
        for room in all_rooms.values():
            if room.capacity < session.total_student_count: continue
            if session.session_type == 'Lab':
                if room.type_of_space != session.course.lab_type: continue
            elif session.session_type == 'Lecture':
                if room.type_of_space in EXCLUDED_LECTURE_SPACES: continue
                if not session.is_small_group and room.room_type != 'Lecture': continue
            valid_rooms.append(room)
        return valid_rooms
    def _filter_instructors(self, session, all_instructors):
        course_id = session.course.course_id
        return [inst for inst in all_instructors.values() if course_id in inst.qualified_courses]
    def __repr__(self):
        return (f"Domain for {self.variable.session_id}: "
                f"T={len(self.timeslot_sequences)}, R={len(self.rooms)}, I={len(self.instructors)}")

class DomainBuilder:
    def __init__(self, model_data):
        self.model_data = model_data
    def build_all_domains(self, variables):
        print(f"\n--- Starting Domain Generation for {len(variables)} variables ---")
        unsolvable_count = 0
        for var in variables:
            var.domain = Domain(var, self.model_data)
            if not var.domain.timeslot_sequences or not var.domain.rooms or not var.domain.instructors:
                unsolvable_count += 1
                if unsolvable_count < 10: print(f"--- FATAL WARNING: {var!r} has an empty domain.")
        if unsolvable_count > 0:
            print(f"--- Domain Generation Complete with {unsolvable_count} UNSOLVABLE variables. ---")
        else:
            print("--- Domain Generation Complete. All variables have a valid domain. ---")

print("--- End of Prerequisite Code (Part 3) ---")


# --- ************************************** ---
# --- STEP 4: PHASE 1 SOLVER (Copied)        ---
# --- ************************************** ---

@dataclass
class Assignment:
    session: ClassSession
    timeslot_sequence: list
    room: Room
    instructor: Instructor

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
        self.model_data = model_data # Save for LCV

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
                    penalty += 10 # High penalty

            # 2. Penalty for Not Preferred Instructor
            if inst.instructor_id not in var.preferred_instructors and var.preferred_instructors:
                penalty += 5 # Medium penalty

            # 3. Reward for Preferred Instructor (negative penalty)
            if inst.instructor_id in var.preferred_instructors:
                penalty -= 20 # Strong reward

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

print("--- End of Prerequisite Code (Part 4) ---")


# --- ************************************** ---
# --- STEP 5: PHASE 2 & OUTPUT (NEW CODE)    ---
# --- ************************************** ---

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

                if gap_size == 2: # e.g., busy at slot 1, then slot 3. Gap is 1 slot.
                    gap_penalty += 1
                elif gap_size == 3: # e.g., busy at 1, then 4. Gap is 2 slots.
                    gap_penalty += 3 # Heavier penalty for larger gap
                elif gap_size > 3:
                    gap_penalty += 5
        return gap_penalty

class IterativeSolver:
    """
    Phase 2: Takes a valid solution and tries to improve it
    using a simple hill-climbing metaheuristic.
    """
    def __init__(self, solution, state, evaluator, model_data, iterations=10000):
        self.current_solution = solution # List of Assignments
        self.current_state = state # TimetableState object
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
                continue # Could not find a valid swap

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
        neighbor_solution = list(self.current_solution) # Shallow copy of list

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
            return None, None # Swap failed

        # Add new_a1 to the state so we can check new_a2 against it
        neighbor_state.add_assignment(new_a1)

        # Check if new_a2 is valid for session a2
        valid_a2 = (new_a2.instructor in a2.session.domain.instructors and
                    new_a2.room in a2.session.domain.rooms and
                    new_a2.timeslot_sequence in a2.session.domain.timeslot_sequences and
                    neighbor_state.is_consistent(new_a2.session, new_a2.timeslot_sequence, new_a2.room, new_a2.instructor))

        if not valid_a2:
            return None, None # Swap failed

        # 4. If both are valid, finalize the neighbor
        neighbor_state.add_assignment(new_a2)

        # Update the neighbor solution list
        neighbor_solution.remove(a1)
        neighbor_solution.remove(a2)
        neighbor_solution.append(new_a1)
        neighbor_solution.append(new_a2)

        return neighbor_solution, neighbor_state

def save_solution_to_csv(solution, model_data, filename):
    """Converts the list of Assignment objects into a readable CSV."""
    print(f"\n--- Saving solution to {filename} ---")

    # We need the TimeSlot objects for start/end times
    timeslots_map = model_data['timeslots']

    output_data = []
    for assignment in solution:
        session = assignment.session

        # Get timeslot info
        first_slot_id = assignment.timeslot_sequence[0]
        last_slot_id = assignment.timeslot_sequence[-1]

        start_time = timeslots_map[first_slot_id].start_time
        end_time = timeslots_map[last_slot_id].end_time
        day = timeslots_map[first_slot_id].day

        # Get section info
        section_ids = ", ".join([s.section_id for s in session.sections])

        output_data.append({
            "Day": day,
            "StartTime": start_time,
            "EndTime": end_time,
            "CourseID": session.course.course_id,
            "CourseName": session.course.name,
            "Type": session.session_type,
            "Instructor": assignment.instructor.name,
            "Room": assignment.room.room_id,
            "Sections": section_ids,
            "StudentCount": session.total_student_count
        })

    # Create DataFrame and save
    df = pd.DataFrame(output_data)
    # Sort for readability
    df = df.sort_values(by=["Day", "StartTime"])

    try:
        df.to_csv(filename, index=False)
        print(f"Successfully saved timetable to {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")


# --- ************************************** ---
# --- STEP 6: EXECUTION (MAIN)               ---
# --- ************************************** ---

if __name__ == "__main__":

    # --- 1. Load Data ---
    print("--- Running Data Loader ---")
    loader = DataLoader(FILE_PATHS)
    model_data = loader.load_all()

    if model_data:
        print("\n--- Data Loading Successful ---")

        # --- 2. Generate Variables ---
        var_generator = VariableGenerator(model_data, max_group_capacity=75)
        all_variables = var_generator.generate_all_variables()

        # --- 3. Build Domains ---
        domain_builder = DomainBuilder(model_data)
        domain_builder.build_all_domains(all_variables)

        if any(not v.domain.instructors or not v.domain.rooms or not v.domain.timeslot_sequences for v in all_variables):
            print("\n--- PROBLEM IS UNSOLVABLE: Cannot start solver. ---")
            print("Please fix the 'FATAL WARNING' errors above by correcting the data.")
        else:
            # --- 4. Run Phase 1 Solver ---
            solver = BacktrackingSolver(all_variables, model_data)
            phase1_solution, phase1_state = solver.solve()

            if phase1_solution:
                # --- 5. Run Phase 2 Optimizer ---
                evaluator = CostEvaluator(model_data)
                optimizer = IterativeSolver(
                    phase1_solution,
                    phase1_state,
                    evaluator,
                    model_data,
                    iterations=20000 # Increase iterations for better results
                )
                final_optimized_solution = optimizer.optimize()

                # --- 6. Save Final Solution ---
                save_solution_to_csv(final_optimized_solution, model_data, OUTPUT_FILE)
            else:
                print("\nNo solution found by Phase 1. Cannot optimize or save.")
                