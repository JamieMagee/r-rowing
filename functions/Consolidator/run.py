from os import environ

import praw

reddit = praw.Reddit(
    client_id=environ['CLIENT_ID'],
    client_secret=environ['CLIENT_SECRET'],
    username=environ['USERNAME'],
    password=environ['PASSWORD'],
    user_agent='RowingFlair by /u/Jammie1')

rowing_flair = reddit.subreddit('rowing').flair()
flair_in_use = set()
for flair in rowing_flair:
  if flair['flair_css_class'] is None:
    continue
  flair_in_use.add(int(flair['flair_css_class']))
print(flair_in_use ^ set(range(1, 1133)))
