from datetime import datetime, timedelta


class Event:
    def __init__(self, code, creator, title, start_date, duration_time, max_members, text, deadline, tags=None):
        self.code = code
        self.title = title
        self.start_date = start_date
        self.duration_time = duration_time
        self.max_members = max_members
        self.text = text
        self.tags = tags
        self.deadline = deadline

        if self.tags is None:
            self.tags = []

        self.creator = creator

        self.participants = []

    def __str__(self):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return '**ID:** {} **Title:** {} **Start:** {} **Deadline:** {} **Members:** {}/{}'.format(self.code,
                                                                                                   self.title,
                                                                                                   days[
                                                                                                       self.start_date.weekday()] + ' ' + self.start_date.strftime(
                                                                                                       '%I:%M%p %d-%m-%Y'),
                                                                                                   days[
                                                                                                       self.start_date.weekday()] + ' ' + self.start_date.strftime(
                                                                                                       '%I:%M%p %d-%m-%Y'),
                                                                                                   self.participants.__len__(),
                                                                                                   self.max_members)
