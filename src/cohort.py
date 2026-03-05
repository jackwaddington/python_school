class Cohort:
    def __init__(self, number, intake_week, students):
        self.number = number
        self.intake_week = intake_week
        self.students = students
        self.is_rough = False

    def __str__(self):
        return f"Cohort {self.number} (intake week {self.intake_week}, {len(self.students)} students)"
