# =====================================
# data_loader/loader.py
# Loads all CSV and Excel data sources
# =====================================

import pandas as pd
import ast
from models.entities import Course, Room, Instructor, TimeSlot, Section, AvailableCourse


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
