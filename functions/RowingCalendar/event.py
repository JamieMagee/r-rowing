import re
from datetime import datetime


class Event:

    def __init__(self, date, name, link, location=''):
        try:
            self.date = datetime.strptime(date, '%Y-%m-%d')
        except:
            date = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date)
            self.date = datetime.strptime(date, '%A %d %B %Y')
        self.name = name
        self.link = link
        self.location = location

    def table_row(self):
        return f'|[{self.name}]({self.link})|{self.date.strftime("%d %B")}|{self.location}|\n'
