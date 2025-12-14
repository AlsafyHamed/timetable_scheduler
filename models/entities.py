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
