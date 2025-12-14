"""
API Service Layer
Handles data loading and business logic for the REST API
"""

import json
from collections import defaultdict
from data_loader.loader import DataLoader


class TimetableAPIService:
    """Service class to load and provide timetable data for API endpoints"""

    def __init__(self, json_file_path, csv_file_paths):
        self.json_file_path = json_file_path
        self.csv_file_paths = csv_file_paths
        self.timetable_data = None
        self.model_data = None
        self._load_data()

    def _load_data(self):
        """Load timetable data from JSON and CSV files"""
        # Load JSON timetable data
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.timetable_data = json.load(f)
            print(f"Loaded timetable data from {self.json_file_path}")
        except FileNotFoundError:
            print(f"Warning: {self.json_file_path} not found. Some endpoints may not work.")
            self.timetable_data = {
                "metadata": {},
                "courses": [],
                "instructors": [],
                "sections": [],
                "rooms": [],
                "timeslots": [],
                "schedule": []
            }

        # Load model data from CSV files
        loader = DataLoader(self.csv_file_paths)
        self.model_data = loader.load_all()

    def get_all_levels(self):
        """Get all unique levels with their departments and specializations"""
        if not self.timetable_data:
            return []

        levels_dict = defaultdict(lambda: {
            "level": 0,
            "departments": set(),
            "specializations": set(),
            "sections": []
        })

        for section in self.timetable_data.get("sections", []):
            level = section["level"]
            dept = section["department"]
            spec = section["specialization"]

            levels_dict[level]["level"] = level
            levels_dict[level]["departments"].add(dept)
            levels_dict[level]["specializations"].add(spec)
            levels_dict[level]["sections"].append(section["section_id"])

        # Convert sets to lists for JSON serialization
        result = []
        for level_num in sorted(levels_dict.keys()):
            data = levels_dict[level_num]
            result.append({
                "level": data["level"],
                "departments": sorted(list(data["departments"])),
                "specializations": sorted(list(data["specializations"])),
                "section_count": len(data["sections"]),
                "sections": sorted(data["sections"])
            })

        return result

    def get_all_instructors(self):
        """Get all instructors with their details"""
        if not self.timetable_data:
            return []

        instructors = self.timetable_data.get("instructors", [])

        # Add schedule information for each instructor
        for instructor in instructors:
            instructor_id = instructor["instructor_id"]
            schedule = [
                entry for entry in self.timetable_data.get("schedule", [])
                if entry["instructor_id"] == instructor_id
            ]
            instructor["schedule"] = schedule
            instructor["total_teaching_hours"] = len(schedule)

        return instructors

    def get_instructor_by_id(self, instructor_id):
        """Get specific instructor details by ID"""
        instructors = self.get_all_instructors()
        for instructor in instructors:
            if instructor["instructor_id"] == instructor_id:
                return instructor
        return None

    def get_all_courses(self):
        """Get all courses"""
        return self.timetable_data.get("courses", [])

    def get_course_schedule(self, course_id):
        """Get schedule for a specific course with all time slots"""
        schedule = [
            entry for entry in self.timetable_data.get("schedule", [])
            if entry["course_id"] == course_id
        ]

        # Get course info
        course_info = next(
            (c for c in self.timetable_data.get("courses", []) if c["course_id"] == course_id),
            None
        )

        return {
            "course": course_info,
            "schedule": schedule,
            "total_sessions": len(schedule)
        }

    def get_course_details(self, course_id):
        """Get comprehensive course details including instructors and students"""
        schedule = [
            entry for entry in self.timetable_data.get("schedule", [])
            if entry["course_id"] == course_id
        ]

        # Get course info
        course_info = next(
            (c for c in self.timetable_data.get("courses", []) if c["course_id"] == course_id),
            None
        )

        if not course_info:
            return None

        # Get unique instructors teaching this course
        instructors = {}
        for entry in schedule:
            inst_id = entry["instructor_id"]
            if inst_id not in instructors:
                instructors[inst_id] = {
                    "instructor_id": inst_id,
                    "instructor_name": entry["instructor_name"],
                    "sessions": []
                }
            instructors[inst_id]["sessions"].append({
                "day": entry["day"],
                "start_time": entry["start_time"],
                "end_time": entry["end_time"],
                "session_type": entry["session_type"],
                "room": entry["room_id"],
                "sections": entry["sections"]
            })

        # Get unique sections taking this course
        sections_set = set()
        total_students = 0
        for entry in schedule:
            for section_id in entry["sections"]:
                sections_set.add(section_id)

        # Get section details
        sections_details = []
        for section_id in sections_set:
            section_info = next(
                (s for s in self.timetable_data.get("sections", []) if s["section_id"] == section_id),
                None
            )
            if section_info:
                sections_details.append(section_info)
                total_students += section_info["student_count"]

        return {
            "course": course_info,
            "instructors": list(instructors.values()),
            "sections": sections_details,
            "total_students": total_students,
            "schedule": schedule,
            "total_sessions": len(schedule)
        }

    def get_timetable(self, day=None, level=None, section=None):
        """Get complete timetable with optional filters"""
        schedule = self.timetable_data.get("schedule", [])

        # Apply filters
        if day:
            schedule = [entry for entry in schedule if entry["day"].lower() == day.lower()]

        if level:
            schedule = [
                entry for entry in schedule
                if any(
                    s.startswith(f"CSIT-{level}-")
                    for s in entry["sections"]
                )
            ]

        if section:
            schedule = [
                entry for entry in schedule
                if section in entry["sections"]
            ]

        return {
            "schedule": schedule,
            "total_entries": len(schedule)
        }

    def get_all_sections(self):
        """Get all sections"""
        return self.timetable_data.get("sections", [])

    def get_all_rooms(self):
        """Get all rooms"""
        return self.timetable_data.get("rooms", [])

    def get_metadata(self):
        """Get timetable metadata"""
        return self.timetable_data.get("metadata", {})
