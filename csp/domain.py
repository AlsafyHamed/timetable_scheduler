class Domain:
    def __init__(self, session_variable, model_data):
        self.variable = session_variable
        self.timeslot_sequences = self._generate_consecutive_sequences(
            model_data['timeslots_df'], session_variable.duration_slots)
        self.rooms = self._filter_rooms(session_variable, model_data['rooms'])
        self.instructors = self._filter_instructors(session_variable, model_data['instructors'])

    # (rest of helper methods...)

class DomainBuilder:
    def __init__(self, model_data):
        self.model_data = model_data
    def build_all_domains(self, variables):
        for var in variables:
            var.domain = Domain(var, self.model_data)
