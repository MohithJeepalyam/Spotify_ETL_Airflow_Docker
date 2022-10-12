from dotenv import load_dotenv
import os

import numpy as np
import pandas as pd

import psycopg2
from sqlalchemy import create_engine

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_url = "https://localhost"

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint

token = SpotifyOAuth(client_id = client_id,
             client_secret = client_secret,
             redirect_uri = redirect_url,
             scope = "user-read-recently-played"
)


sp = spotipy.Spotify(auth_manager = token)
recently_played_data = sp.current_user_recently_played(after = 1661117400000)

# print(recently_played_data['items'])

if len(recently_played_data) == 0:
    sys.exit("No tracks to add on this day!")


album_list = []
for row in recently_played_data['items']:
    album_id = row['track']['album']['id']
    album_name = row['track']['album']['name']
    album_release_date = row['track']['album']['release_date']
    album_total_tracks = row['track']['album']['total_tracks']
    album_url = row['track']['album']['external_urls']['spotify']
    album_element = {'album_id':album_id,'name':album_name,'release_date': album_release_date,
                        'total_tracks':album_total_tracks,'url':album_url}
    album_list.append(album_element)

# print(album_list)


artist_dict = {}
id_list = []
name_list = []
url_list = []
for item in recently_played_data['items']:
    for key,value in item.items():
        if key == "track":
            for data_point in value['artists']:
                id_list.append(data_point['id'])
                name_list.append(data_point['name'])
                url_list.append(data_point['external_urls']['spotify'])
artist_dict = {'artist_id':id_list,'name':name_list,'url':url_list}

# print(artist_dict)


song_list = []
for row in recently_played_data['items']:
    song_id = row['track']['id']
    song_name = row['track']['name']
    song_duration = row['track']['duration_ms']
    song_url = row['track']['external_urls']['spotify']
    song_popularity = row['track']['popularity']
    song_time_played = row['played_at']
    album_id = row['track']['album']['id']
    artist_id = row['track']['album']['artists'][0]['id']
    song_element = {'song_id':song_id,'song_name':song_name,'duration_ms':song_duration,'url':song_url,
                    'popularity':song_popularity,'date_time_played':song_time_played,'album_id':album_id,
                    'artist_id':artist_id
                }
    song_list.append(song_element)

# print(song_list)


#Album = We can also just remove duplicates here. We dont want to load two of the same albums just to have SQL drop it later
album_df = pd.DataFrame.from_dict(album_list)
album_df = album_df.drop_duplicates(subset=['album_id'])

#Artist = We can also just remove duplicates here. We dont want to load two of the same artists just to have SQL drop it later
artist_df = pd.DataFrame.from_dict(artist_dict)
artist_df = artist_df.drop_duplicates(subset=['artist_id'])

#Song Dataframe
song_df = pd.DataFrame.from_dict(song_list)
#date_time_played is an object (data type) changing to a timestamp
song_df['date_time_played'] = pd.to_datetime(song_df['date_time_played'])
#converting to my timezone of Central
song_df['date_time_played'] = song_df['date_time_played'].dt.tz_convert('US/Central')
#I have to remove the timezone part from the date/time/timezone.
song_df['date_time_played'] = song_df['date_time_played'].astype(str).str[:-7]
song_df['date_time_played'] = pd.to_datetime(song_df['date_time_played'])
#Creating a Unix Timestamp for Time Played. This will be one half of our unique identifier
song_df['UNIX_Time_Stamp'] = (song_df['date_time_played'] - pd.Timestamp("1970-01-01"))//pd.Timedelta('1s')
# I need to create a new unique identifier column because we dont want to be insterting the same song played at the same song
# I can have the same song multiple times in my database but I dont want to have the same song played at the same time
song_df['unique_identifier'] = song_df['song_id'] + "-" + song_df['UNIX_Time_Stamp'].astype(str)
song_df = song_df[['unique_identifier','song_id','song_name','duration_ms','url','popularity','date_time_played','album_id','artist_id']]
song_df.to_csv(r"/Users/Mohit/Downloads/test.csv")
#NOW We are going to Load PostgresSQL

#Loading the data into the Temporary Table
conn = psycopg2.connect(host = "",port="", dbname = "")
cur = conn.cursor()
engine = create_engine('postgresql+psycopg2://@/')
conn_eng = engine.raw_connection()
cur_eng = conn_eng.cursor()

