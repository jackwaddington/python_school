class Exam:

    def __init__(self, course_subject):
        self.course_subject = course_subject
        self.questions = []

    def __str__(self):
        return f"{self.course_subject}, {self.questions}"
