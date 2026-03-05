class Course:

    def __init__(self, subject, field):
        self.subject = subject
        self.field = field
        self.material = None
        self.exam = None
        self.enrolled_students = []
        self.required_passes = 0

    def __str__(self):
        return f"{self.subject} - {len(self.enrolled_students)} students enrolled"
