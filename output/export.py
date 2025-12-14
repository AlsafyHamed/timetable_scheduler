import pandas as pd
import json
from datetime import datetime

def save_solution_to_csv(solution, model_data, filename):
    timeslots_map = model_data['timeslots']
    output_data = []
    for assignment in solution:
        session = assignment.session
        first_slot_id = assignment.timeslot_sequence[0]
        last_slot_id = assignment.timeslot_sequence[-1]
        start_time = timeslots_map[first_slot_id].start_time
        end_time = timeslots_map[last_slot_id].end_time
        day = timeslots_map[first_slot_id].day
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
    pd.DataFrame(output_data).sort_values(by=["Day", "StartTime"]).to_csv(filename, index=False)
    print(f"Saved timetable to {filename}")

def save_solution_to_json(solution, model_data, filename):
    """
    Save the timetable solution to a JSON file with complete data structure.
    Includes courses, instructors, sections, rooms, timeslots, and schedule entries.
    """
    timeslots_map = model_data['timeslots']

    # Build schedule entries
    schedule_entries = []
    for assignment in solution:
        session = assignment.session
        first_slot_id = assignment.timeslot_sequence[0]
        last_slot_id = assignment.timeslot_sequence[-1]
        start_time = timeslots_map[first_slot_id].start_time
        end_time = timeslots_map[last_slot_id].end_time
        day = timeslots_map[first_slot_id].day

        schedule_entries.append({
            "day": day,
            "start_time": start_time,
            "end_time": end_time,
            "course_id": session.course.course_id,
            "course_name": session.course.name,
            "session_type": session.session_type,
            "instructor_id": assignment.instructor.instructor_id,
            "instructor_name": assignment.instructor.name,
            "room_id": assignment.room.room_id,
            "room_capacity": assignment.room.capacity,
            "room_type": assignment.room.type_of_space,
            "sections": [s.section_id for s in session.sections],
            "student_count": session.total_student_count,
            "timeslot_ids": assignment.timeslot_sequence
        })

    # Build courses data
    courses_data = []
    for course_id, course in model_data['courses'].items():
        courses_data.append({
            "course_id": course.course_id,
            "name": course.name,
            "lecture_duration": course.lecture_duration,
            "lab_duration": course.lab_duration,
            "lab_type": course.lab_type
        })

    # Build instructors data
    instructors_data = []
    for instructor_id, instructor in model_data['instructors'].items():
        instructors_data.append({
            "instructor_id": instructor.instructor_id,
            "name": instructor.name,
            "qualified_courses": list(instructor.qualified_courses),
            "not_preferred_slots": list(instructor.not_preferred_slots)
        })

    # Build sections data
    sections_data = []
    for section_id, section in model_data['sections'].items():
        sections_data.append({
            "section_id": section.section_id,
            "department": section.department,
            "level": section.level,
            "specialization": section.specialization,
            "student_count": section.student_count
        })

    # Build rooms data
    rooms_data = []
    for room_id, room in model_data['rooms'].items():
        rooms_data.append({
            "room_id": room.room_id,
            "capacity": room.capacity,
            "room_type": room.room_type,
            "type_of_space": room.type_of_space
        })

    # Build timeslots data
    timeslots_data = []
    for slot_id, timeslot in timeslots_map.items():
        timeslots_data.append({
            "slot_id": timeslot.slot_id,
            "day": timeslot.day,
            "start_time": timeslot.start_time,
            "end_time": timeslot.end_time
        })

    # Combine all data
    timetable_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_sessions": len(schedule_entries)
        },
        "courses": courses_data,
        "instructors": instructors_data,
        "sections": sections_data,
        "rooms": rooms_data,
        "timeslots": timeslots_data,
        "schedule": sorted(schedule_entries, key=lambda x: (x["day"], x["start_time"]))
    }

    # Write to JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(timetable_data, f, indent=2, ensure_ascii=False)

    print(f"Saved timetable data to {filename}")
