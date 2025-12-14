# =====================================
# csp/domain.py
# Domain generation for CSP variables
# =====================================


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
