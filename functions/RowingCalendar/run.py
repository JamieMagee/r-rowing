import logging
import re
from datetime import datetime, timedelta
from os import environ

import praw
import requests
from event import Event
from lxml import html

logger = logging.getLogger(__name__)


def parse_british_rowing(page):
    tree = html.fromstring(page)
    br_events = []
    for event in tree.xpath('//div[@class="rich-results__result__content"]'):
        name = event.find('h3').text
        date = event.find('p/time').text

        link = ''
        try:
            link = event.find('div/a').get('href')
        except:
            logger.warning(f'No link for {name}')

        br_events.append(Event(
            date,
            name,
            link
        ))
    return br_events


def parse_regatta_central(json):
    data = json['data']
    rc_events = []
    for event in data:
        rc_events.append(Event(
            event['startDate'],
            event['full_name'],
            f'https://www.regattacentral.com/regatta/?job_id={event["job_id"]}',
            event['location']
        ))
    return rc_events


def generate_table(events):
    table = '|**Race**|**Date**|**Venue**|\n|-|-|-|\n'
    for event in events:
        table += event.table_row()
    return table


def filter_by_date(events):
    start_date = datetime.now()
    end_date = start_date + timedelta(weeks=1)
    return sorted([e for e in events if start_date <= e.date <= end_date], key=lambda e: e.date)


def set_sidebar(out):
    logger.info('Logging in')
    r = praw.Reddit(client_id=environ['CLIENT_ID'],
                    client_secret=environ['CLIENT_SECRET'],
                    username=environ['USERNAME'],
                    password=environ['PASSWORD'],
                    user_agent='RowingFlair by /u/Jammie1')

    sub = r.subreddit('Jammie1')
    settings = sub.mod.settings()
    logger.info('Login successful')

    desc = settings['description']
    table = re.compile(r'\*\*Upcoming Races\*\*.*', re.DOTALL)
    desc = (re.sub(table, out, desc))
    sub.mod.update(description=desc)
    logger.info('Updated sidebar')


rc = 'https://www.regattacentral.com/v3/regattas/jobs?resultsOnly=false&country={}&state=all&year=0&type=all'
br = 'https://www.britishrowing.org/events/events-calendar/'
countries = ['AU', 'CA', 'DE', 'IT', 'US', 'DK', 'HK', 'IE', 'NO', 'SI']
events = []

page = requests.get(br).text
logger.info('Parsing British Rowing calendar')
events.extend(parse_british_rowing(page))

for country in countries:
    logger.info('Fetching JSON')
    json = requests.get(rc.format(country, datetime.now().year)).json()
    logger.info(f'Parsing Regatta Central calendar for {country}')
    events.extend(parse_regatta_central(json))

events = filter_by_date(events)

logger.info('Generating table')
markdown = '\n**Upcoming Races**\n\n' + generate_table(events)
logger.info('Updating sidebar')
if len(markdown) <= 5120:
    set_sidebar(markdown)
else:
    logger.error('Table too large')
