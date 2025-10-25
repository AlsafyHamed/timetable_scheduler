import pandas as pd

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
