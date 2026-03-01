class Newsletter:

    def __init__(self, date, newsletter_type, recipients, content):
        self.date = date
        self.newsletter_type = newsletter_type
        self.recipients = recipients
        self.content = content

    def __str__(self):
        return f"{self.date} - {self.newsletter_type} - {self.content}"
