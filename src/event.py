class Event:

    def __init__(self, date, title, description):
        self.date = date
        self.title = title
        self.description = description

    def __str__(self):
        return f"{self.date} - {self.title} - {self.description}"
