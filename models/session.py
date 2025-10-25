class ClassSession:
    _session_counter = 0
    def __init__(self, course, session_type, duration_slots):
        ClassSession._session_counter += 1
        self.session_id = f"S{ClassSession._session_counter}"
        self.course = course
        self.session_type = session_type
        self.duration_slots = duration_slots
        self.sections = []
        self.preferred_instructors = set()
        self.total_student_count = 0
        self.is_small_group = False
        self.domain = None
    def add_section(self, section):
        if section not in self.sections:
            self.sections.append(section)
            self.total_student_count += section.student_count
    def set_small_group_flag(self, max_capacity):
        self.is_small_group = self.total_student_count < max_capacity

class VariableGenerator:
    def __init__(self, model_data, max_group_capacity=75):
        self.model_data = model_data
        self.max_capacity = max_group_capacity
        self.all_variables = []
    # (rest of variable generation methods)
