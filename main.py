"""
    @Author: LunaEspindola
    @Date: 2024-04-03
    @Description: A Twitch bot that allows viewers to add songs to a Spotify playlist, skip the current song, delete a song from the playlist, view the current playlist, pause the current song, and resume the current song.
"""

# Import libraries
import asyncio
from twitchio.ext import commands
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# load environment variables
load_dotenv()

# Twitch Bot Configuration
TWITCH_BOT_USERNAME = 'BunnySongBot'
TWITCH_BOT_TOKEN = os.getenv('TWITCH_BOT_TOKEN') 
TWITCH_CHANNEL = os.getenv('TWITCH_CHANNEL')

# Spotify API credentials
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# Scope for required permissions
SCOPE = 'playlist-modify-private playlist-modify-public'

# Spotify username and playlist ID
USERNAME = 'Singabunny'
PLAYLIST_ID = '1wUeRHhzRuw0mXPRiX9wMG'  # Corrected playlist ID

# Initialize Spotipy with OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE))

# Function to search for a track
def search_track(track_name):
    result = sp.search(q=track_name, limit=1)
    if result['tracks']['items']:
        return result['tracks']['items'][0]['uri']
    else:
        return None

# Function to add a track to a playlist
def add_track_to_playlist(track_uri):
    sp.playlist_add_items(playlist_id=PLAYLIST_ID, items=[track_uri])
    
# Function to get the current track in the playlist
def get_current_track():
    playlist = sp.playlist_items(playlist_id=PLAYLIST_ID)
    return playlist['items'][0]['track']['name']

# Function to skip the current track in the playlist
def skip_current_track():
    current_track = get_current_track()
    sp.playlist_remove_all_occurrences_of_items(playlist_id=PLAYLIST_ID, items=[search_track(current_track)])
    
# Function delete a track from the playlist
def delete_track(track_uri):
    sp.playlist_remove_all_occurrences_of_items(playlist_id=PLAYLIST_ID, items=[track_uri])
    
# Function to delete all tracks from the playlist
def delete_all_tracks():
    playlist = sp.playlist_items(playlist_id=PLAYLIST_ID)
    track_uris = [track['track']['uri'] for track in playlist['items']]
    sp.playlist_remove_all_occurrences_of_items(playlist_id=PLAYLIST_ID, items=track_uris)
    
# Function to get the current playlist
def get_playlist():
    playlist = sp.playlist_items(playlist_id=PLAYLIST_ID)
    return [track['track']['name'] for track in playlist['items']]

# Function to pause the current track
def pause_track():
    sp.pause_playback()
    
# Function to resume the current track
def resume_track():
    sp.start_playback()

# Twitch Bot Setup
bot = commands.Bot(
    token=TWITCH_BOT_TOKEN,
    nick=TWITCH_BOT_USERNAME,
    prefix='song ',
    initial_channels=[TWITCH_CHANNEL]
)

# Define Twitch Command
@bot.command(name='add')
async def spotify_command(ctx):
    track_name = ctx.message.content.split(' ', 1)[1]
    track_uri = search_track(track_name)
    if track_uri:
        add_track_to_playlist(track_uri)
        await ctx.send(f"{track_name} added successfully to the playlist!")
    else:
        await ctx.send(f"{track_name} not found.")
        
@bot.command(name='skip')
async def skip_command(ctx):
    skip_current_track()
    await ctx.send("Current track skipped successfully!")
    
@bot.command(name='delete')
async def delete_command(ctx):
    track_name = ctx.message.content.split(' ', 1)[1]
    track_uri = search_track(track_name)
    if track_uri:
        delete_track(track_uri)
        await ctx.send(f"{track_name} deleted successfully from the playlist!")
    else:
        await ctx.send(f"{track_name} not found.")
        
    # @bot.command(name='delete_all')
    # async def delete_all_command(ctx):
    #     delete_all_tracks()
    #     await ctx.send("All tracks deleted successfully from the playlist!")
    
@bot.command(name='playlist')
async def playlist_command(ctx):
    playlist = get_playlist()
    await ctx.send(f"Current Playlist: {', '.join(playlist)}")
    
@bot.command(name='pause')
async def pause_command(ctx):
    pause_track()
    await ctx.send("Track paused successfully!")
    
@bot.command(name='resume')
async def resume_command(ctx):
    resume_track()
    await ctx.send("Track resumed successfully!")
 
@bot.command(name='help')
async def help_command(ctx):
    await ctx.send("Commands: song add <track>, song skip, song delete <track>, song playlist, song pause, song resume, song help")
    

# Create an event loop
loop = asyncio.get_event_loop()

# Run the Bot
async def main():
    await bot.start()

# Start the bot using the event loop
loop.create_task(main())

# Keep the event loop running
loop.run_forever()