import random

class Student:
    def __init__(self, first_name, last_name, email, pronouns):
        self.first_name = first_name
        self.last_name = last_name
        self.pronouns = pronouns
        self.allergies = None
        self.next_of_kin = None
        self.email = email
        self.dropped_out = False
        self.graduated = False
        self.ability = round(random.uniform(0.3, 0.9), 2)
        self.course_index = 0
        self.course_passes = {}
        self.cohort = None

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.pronouns})"
