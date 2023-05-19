import requests
import os
import pytz
import decimal
from flask import json
from config import Config
from music_api.spotify import Spotify

api_key = Config.YOUTUBE_API_KEY


CLIENT_ID  = Config.CLIENT_ID
CLIENT_SECRET = Config.CLIENT_SECRET

my_spotify_client = Spotify(CLIENT_ID, CLIENT_SECRET)

def first(iterable, default = None, condition = lambda x: True):
    """
    Returns  the first item in the `iterable` that
    satisfies the `condition`.

    If the condition is not given, returns the first item of
    the iterable.

    If the `default` argument is given and the iterable is empty,
    or if it has no items matching the condition, the `default` argument
    is returned if it matches the condition.

    The `default` argument being None is the same as it not being given.

    Raises `StopIteration` if no item satisfying the condition is found
    and default is not given or doesn't satisfy the condition.

    >>> first( (1,2,3), condition=lambda x: x % 2 == 0)
    2
    >>> first(range(3, 100))
    3
    >>> first( () )
    Traceback (most recent call last):
    ...
    StopIteration
    >>> first([], default=1)
    1
    >>> first([], default=1, condition=lambda x: x % 2 == 0)
    Traceback (most recent call last):
    ...
    StopIteration
    >>> first([1,3,5], default=1, condition=lambda x: x % 2 == 0)
    Traceback (most recent call last):
    ...
    StopIteration
    """

    try:
        return next(x for x in iterable if condition(x))
    except StopIteration:
        if default is not None and condition(default):
            return default
        else:
            raise


def search_videos(search_term, max_results=10):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults={max_results}&q={search_term}&key={api_key}&videoCategoryId=10&type=video"
    response = requests.get(url)
    data = response.json()
    
    videos = []
    # print(data)
    for item in data['items']:
        video = {
            'title': item['snippet']['title'],
            'youtube_id': item['id']['videoId'],
            'spotify_id': '',
            'album_name': item['snippet']['channelTitle'], 
            'album_image': item['snippet']['thumbnails']['default']['url'],
            'artists': '',
            'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        }
        videos.append(video)
    
    return videos

import random
import string

def get_random_search():
    # A list of all characters that can be chosen.
    characters = string.ascii_lowercase

    # Gets a random character from the characters string.
    random_character = random.choice(characters)
    random_search = ''

    # Places the wildcard character at the beginning, or both beginning and end, randomly.
    switch = round(random.random())
    if switch == 0:
        random_search = random_character + '%'
    elif switch == 1:
        random_search = '%' + random_character + '%'
    # random_search = random_character 
    
    
    random_offset = random.randint(0, 9)


    return random_search, random_offset




def to_est(dt):
    utc_dt = pytz.utc.localize(dt)
    est = pytz.timezone('US/Eastern')
    return utc_dt.astimezone(est)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(JSONEncoder, self).default(obj)
