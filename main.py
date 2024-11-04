#!/usr/bin/env python3
from requests.adapters import HTTPAdapter, Retry
import requests
import traceback
import config
import time
import re

print('Starting Goon Patrol v2.0 - Stalking trainvoi')

s = requests.Session()
retries = Retry(total=5, backoff_factor=0.1)
s.mount('https://danbooru.donmai.us', HTTPAdapter(max_retries=retries))

def getFavs():
    try:
        resp = s.get('https://danbooru.donmai.us/users/%s' % config.user_id)
        match = re.search(r'<a rel="nofollow" href="\/posts\?tags=ordfav%3A%s">(.*)<\/a>' % config.username, resp.text)
        return int(match.group(1))
    except Exception as e:
        traceback.print_exception(e)
        return

def send(msg):
    s.post(webhook_url, json={'content': f"{discord_mention} {msg}"})

def main():
    favs = getFavs()
    streak_mins = 0
    streak_pics = 0

    print(f'Initial favorite count: {favs}')
    send(f"Goon Patrol restarted, {config.danbooru_mention} has favourited {favs} pics!")

    while True:
        new = getFavs()
        if not new:
            send(f"Danbooru decided to not give up {config.danbooru_mention}'s favourite count")
            time.sleep(300)
            continue
        print(f'Previous: {favs}, new: {new}')
        if new > favs:
            streak_mins += 5
            streak_pics += new - favs
            send(f"{config.danbooru_mention} favourited {new - favs} more pics ({streak_mins} minute streak, {new} total)")
        elif new < favs:
            streak_mins += 5
            streak_pics -= favs - new
            send(f"{config.danbooru_mention} unfavourited {favs - new} pics ({streak_mins} minute streak, {new} total)")
        elif streak_mins > 5:
            send(f"{config.danbooru_mention} ended his {streak_mins} minute streak with {streak_pics} new favourites!")
            streak_pics = 0
            streak_mins = 0
        else:
            streak_pics = 0
            streak_mins = 0
        favs = new
        time.sleep(300)

try:
    main()
except Exception as e:
    send(config.error_message)
    traceback.print_exception(e)
