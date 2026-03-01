from student import Student
from course import Course

class School:

    def __init__(self, name, description, seats):
        self.name = name
        self.description = description
        self.students = []
        self.courses = []
        self.seats = seats

    def __str__(self):
        return f"{self.name} school of {self.description.strip()}"
