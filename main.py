from data_loader.loader import DataLoader
from models.session import VariableGenerator
from csp.domain import DomainBuilder
from csp.solver_phase1 import BacktrackingSolver
from csp.solver_phase2 import CostEvaluator, IterativeSolver
from output.export import save_solution_to_csv

FILE_PATHS = {
    "courses": "data/Courses.csv",
    "rooms": "data/Rooms.csv",
    "instructors": "data/Instructors.csv",
    "timeslots": "data/TimeSlots.csv",
    "sections": "data/sections_data.xlsx",
    "available_courses": "data/Avilable_Course.csv"
}

OUTPUT_FILE = "final_timetable.csv"

if __name__ == "__main__":
    print("--- Running Data Loader ---")
    loader = DataLoader(FILE_PATHS)
    model_data = loader.load_all()

    if model_data:
        print("\n--- Data Loading Successful ---")

        var_generator = VariableGenerator(model_data, max_group_capacity=75)
        all_variables = var_generator.generate_all_variables()

        domain_builder = DomainBuilder(model_data)
        domain_builder.build_all_domains(all_variables)

        if any(not v.domain.instructors or not v.domain.rooms or not v.domain.timeslot_sequences for v in all_variables):
            print("\n--- PROBLEM IS UNSOLVABLE: Cannot start solver. ---")
        else:
            solver = BacktrackingSolver(all_variables, model_data)
            phase1_solution, phase1_state = solver.solve()

            if phase1_solution:
                evaluator = CostEvaluator(model_data)
                optimizer = IterativeSolver(
                    phase1_solution,
                    phase1_state,
                    evaluator,
                    model_data,
                    iterations=20000
                )
                final_solution = optimizer.optimize()
                save_solution_to_csv(final_solution, model_data, OUTPUT_FILE)
