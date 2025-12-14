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
