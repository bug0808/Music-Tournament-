import random
from collections import defaultdict

class MusicTournament:
    def __init__(self):
        self.songs = []  # List to store songs and their metadata
        self.votes = []  # List to store votes (for future expansion)
        self.match_winners = {}  # Dictionary to track winners
    
    def upload_song(self, song_name, file_path):
        """Upload a song to the tournament."""
        if file_path.endswith(".mp3") and file_path not in [song[1] for song in self.songs]:
            self.songs.append((song_name, file_path))
            print(f"Song '{song_name}' added successfully.")
        else:
            print(f"Invalid or duplicate file: {file_path}")
    
    def get_song_names(self):
        """Get the list of song names."""
        return [song[0] for song in self.songs]  # Returns just the song names
    
    def get_random_pair(self):
        """Select two random songs for the next match."""
        if len(self.songs) < 2:
            return None, None
        random_pair = random.sample(self.songs, 2)
        return random_pair

    def play_song(self, song_name):
        """Play the selected song."""
        song = next((song for song in self.songs if song[0] == song_name), None)
        if song:
            # Code to play the song here (e.g., using Pygame or simpleaudio)
            print(f"Playing: {song_name}")
        else:
            print(f"Song '{song_name}' not found.")
    
    def vote(self, winner_song):
        """Record a vote and eliminate the loser."""
        # Find the losing song (the one not selected as the winner)
        loser_song = next(song for song in self.songs if song[0] != winner_song)
        # Remove the loser from the list of songs
        self.songs = [song for song in self.songs if song[0] != loser_song[0]]
    
    def is_tournament_over(self):
        """Check if the tournament is over."""
        return len(self.songs) == 1  # If only one song remains, the tournament is over
    
    def set_winner(self, match, winner):
        """Sets the winner of a match."""
        if winner not in [match.competitor_a, match.competitor_b]:
            raise ValueError("Winner must be one of the competitors")
        self.match_winners[match] = winner  # Track winner for the match

    def get_winner(self, match):
        """Gets the winner of the match."""
        # Ensure that match is properly passed and handled
        return self.match_winners.get(match, None)  # Returns None if no winner set
