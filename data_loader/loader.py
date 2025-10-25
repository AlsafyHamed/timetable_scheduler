# =====================================
# data_loader/loader.py
# Loads all CSV and Excel data sources
# =====================================

import pandas as pd
import ast
from models.entities import Course, Room, Instructor, TimeSlot, Section, AvailableCourse


class DataLoader:
    def __init__(self, paths):
        """
        paths: dictionary of file paths like:
        {
            "courses": "data/Courses.csv",
            "rooms": "data/Rooms.csv",
            "instructors": "data/Instructors.csv",
            "timeslots": "data/TimeSlots.csv",
            "sections": "data/sections_data.xlsx",
            "available_courses": "data/Avilable_Course.csv"
        }
        """
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
            print("All data loaded successfully ✅")
            return self.model_data
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    # -----------------------------
    # Internal loader functions
    # -----------------------------

    def _load_courses(self):
        df = pd.read_csv(self.paths["courses"])
        courses = []
        for _, row in df.iterrows():
            course = Course(
                row["CourseID"],
                row["Name"],
                row["LectureDuration"],
                row["LabDuration"],
                row["LabType"]
            )
            courses.append(course)
        return courses

    def _load_rooms(self):
        df = pd.read_csv(self.paths["rooms"])
        rooms = []
        for _, row in df.iterrows():
            room = Room(
                row["RoomID"],
                row["Capacity"],
                row["RoomType"],
                row["TypeOfSpace"]
            )
            rooms.append(room)
        return rooms

    def _load_instructors(self):
        df = pd.read_csv(self.paths["instructors"])
        instructors = []
        for _, row in df.iterrows():
            try:
                qualified = ast.literal_eval(row["QualifiedCourses"])
                not_pref = ast.literal_eval(row["NotPreferredSlots"])
            except Exception:
                qualified = []
                not_pref = []
            instructor = Instructor(
                row["InstructorID"],
                row["Name"],
                set(qualified),
                set(not_pref)
            )
            instructors.append(instructor)
        return instructors

    def _load_timeslots(self):
        df = pd.read_csv(self.paths["timeslots"])
        timeslots_dict = {}
        for _, row in df.iterrows():
            slot = TimeSlot(
                row["SlotID"],
                row["Day"],
                row["StartTime"],
                row["EndTime"]
            )
            timeslots_dict[int(row["SlotID"])] = slot
        return timeslots_dict, df

    def _load_sections(self):
        df = pd.read_excel(self.paths["sections"])
        sections = []
        for _, row in df.iterrows():
            section = Section(
                row["SectionID"],
                row["Department"],
                row["Level"],
                row["Specialization"],
                row["StudentCount"]
            )
            sections.append(section)
        return sections

    def _load_available_courses(self):
        df = pd.read_csv(self.paths["available_courses"])
        available_courses = []
        for _, row in df.iterrows():
            try:
                assi_list = ast.literal_eval(row["PreferredAssi"])
            except Exception:
                assi_list = []
            course = AvailableCourse(
                row["Department"],
                row["Level"],
                row["Specialization"],
                row["CourseID"],
                row["PreferredProf"],
                set(assi_list)
            )
            available_courses.append(course)
        return available_courses
