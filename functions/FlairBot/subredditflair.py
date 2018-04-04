import json
import logging
from os import environ

import praw


class SubredditFlair():

  def __init__(self, subreddit):
    self.subreddit = subreddit
    self.r = praw.Reddit(
        client_id=environ['CLIENT_ID'],
        client_secret=environ['CLIENT_SECRET'],
        username=environ['USERNAME'],
        password=environ['PASSWORD'],
        user_agent='RowingFlair by /u/Jammie1')

  def get_messages(self):
    return self.r.inbox.messages(limit=None)

  def get_message_info(self, message):
    return json.loads(message)

  def assign_flair(self, flair)

  def assign_flair(self, user, message_info):
