class ExamResult:
    def __init__(self, student, exam, grade):
        self.student = student
        self.exam = exam
        self.grade = grade

    def __str__(self):
        grades = [(75, "A"), (50, "B"), (25, "C")]
        for threshold, letter in grades:
            if self.grade >= threshold:
                return f"{self.student.first_name} - {letter}"
        return f"{self.student.first_name} - F"
