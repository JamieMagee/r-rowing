from os import environ


from os.path import basename
import tempfile
from urllib.request import urlretrieve, urljoin


import azure.functions as func
import praw
from unidecode import unidecode

r = praw.Reddit(
    client_id=environ["CLIENT_ID"],
    client_secret=environ["CLIENT_SECRET"],
    username=environ["REDDIT_USERNAME"],
    password=environ["REDDIT_PASSWORD"],
    user_agent="RowingFlair by /u/Jammie1",
)

base_url = "http://127.0.0.1:10000/devstoreaccount1/flair/"


def get_emoji_name(name: str, src: str) -> str:
    if not (src.startswith("Solid") or src.startswith("Question")):
        return (basename(src).split(".")[0]).replace("_bigblade", "")
    return "".join(unidecode(e) for e in name if e.isalnum())


def main(msg: func.QueueMessage) -> None:
    msg_body = msg.get_json()

    flair_url = urljoin(base_url, msg_body["src"])
    _, tmp_file = tempfile.mkstemp(suffix=".png")
    urlretrieve(flair_url, tmp_file)

    emoji_name = get_emoji_name(msg_body["name"], msg_body["src"])
    subreddit = r.subreddit("rowing")

    subreddit.emoji.add(emoji_name[:20], tmp_file)
    subreddit.flair.templates.add(f":{emoji_name[:20]}: {emoji_name}", text_editable=True)
