from configparser import ConfigParser
import collections
import re
import time
import os

import praw
from azure.storage import CloudStorageAccount


def replace_all(text, dic):
    text = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', text.strip('\r\n\t\s'))
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

replacements = {'_': ' ',
                '-': ' ',
                'Uni': 'University',
                'front': ''}

if os.path.isfile(os.path.join(os.path.dirname(__file__), 'settings.cfg')):
	config = ConfigParser()
	config.read(os.path.join(os.path.dirname(__file__), 'settings.cfg'))

	subreddit = config.get('reddit', 'subreddit')
	username = config.get('reddit', 'username')
	password = config.get('reddit', 'password')

	storage_account_name = config.get('azure', 'name')
	storage_account_key = config.get('azure', 'key')
else:
    subreddit = os.getenv('SUBREDDIT')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
    storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')

r = praw.Reddit('RowingFlair by /u/Jammie1')
r.login(username, password)

storage_account = CloudStorageAccount(storage_account_name, storage_account_key)

table_service = storage_account.create_table_service()

while True:
    flair_entities = table_service.query_entities('flair', "PartitionKey eq 'flair'")
    flair_entities = [(entity.position, entity.RowKey) for entity in flair_entities]

    flair_users = collections.defaultdict(list)

    for flair in r.get_flair_list(subreddit, limit=None):
        name = ''.join(t[1] for t in flair_entities if str(t[0]) == flair['flair_css_class'])
        name = replace_all(name, replacements)

        flair_users[name].append(flair['user'])

    flair_users = sorted(list(flair_users.items()), key=lambda x: len(x[1]), reverse=True)

    out = ''
    for rowing_club in flair_users:
        out += '* ' + rowing_club[0] + '\n'
        for user in rowing_club[1]:
            out += '  - [' + user + '](/u/' + user + ')\n'
    
    print(out)
    
    r.edit_wiki_page(subreddit, 'flair-stats', out)

    time.sleep(43200)

