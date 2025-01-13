import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import random
import math
import threading

class Competitor:
    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path

class Match:
    def __init__(self, competitor_a, competitor_b):
        self.competitor_a = competitor_a
        self.competitor_b = competitor_b
        self.winner = None

    def set_winner(self, winner):
        """Set the winner of the match."""
        if winner not in [self.competitor_a, self.competitor_b]:
            raise ValueError("Winner must be one of the competitors")
        self.winner = winner

    def get_winner(self):
        """Get the winner of the match."""
        return self.winner


class Bracket:
    def __init__(self, competitors):
        self.competitors = competitors
        self.rounds = []  # List of all rounds
        self.current_round = 0  # Current round index
        self.generate_bracket()

    def generate_bracket(self):
        """Generate the tournament bracket."""
        competitors = [Competitor(name, "") for name in self.competitors]

        # Ensure competitors count is a power of 2
        next_power_of_2 = 2 ** math.ceil(math.log2(len(competitors)))
        while len(competitors) < next_power_of_2:
            competitors.append(Competitor("TBD", ""))

        # First round
        self.rounds.append([Match(competitors[i], competitors[i + 1]) for i in range(0, len(competitors), 2)])

    def get_current_round_matches(self):
        """Return the matches for the current round."""
        return self.rounds[self.current_round]

    def advance_to_next_round(self):
        """Move to the next round with the current round's winners."""
        current_matches = self.get_current_round_matches()
        winners = [match.get_winner() for match in current_matches if match.get_winner()]

        if len(winners) < 2:
            return None  # Tournament is over

        next_round_matches = [Match(winners[i], winners[i + 1] if i + 1 < len(winners) else None) for i in range(0, len(winners), 2)]
        self.rounds.append(next_round_matches)
        self.current_round += 1
        return next_round_matches




class MusicTournamentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Tournament App")
        self.clashes = []  # List to store Clash objects
        self.winners = []  # Initialize winners as an empty list
        pygame.mixer.init()  # Initialize Pygame mixer for audio playback

        self.songs = []  # List of song names
        self.songs_paths = []  # List of song file paths
        self.tournament = None  # Tournament object to manage rounds
        self.song_listbox = tk.Listbox(root)
        self.song_listbox.pack()

        self.upload_button = tk.Button(root, text="Upload Song", command=self.upload_songs)
        self.upload_button.pack()

        self.play_button = tk.Button(root, text="Start Tournament", command=self.start_tournament)
        self.play_button.pack()

        self.vote_button1 = tk.Button(root, text="Vote for Song 1", command=self.vote_for_song_1, state=tk.DISABLED)
        self.vote_button1.pack()

        self.vote_button2 = tk.Button(root, text="Vote for Song 2", command=self.vote_for_song_2, state=tk.DISABLED)
        self.vote_button2.pack()

        self.song1_label = tk.Label(root, text="Song 1:")
        self.song1_label.pack()

        self.song2_label = tk.Label(root, text="Song 2:")
        self.song2_label.pack()

        self.play_song1_button = tk.Button(root, text="Play Song 1", command=self.play_song1, state=tk.DISABLED)
        self.play_song1_button.pack()

        self.play_song2_button = tk.Button(root, text="Play Song 2", command=self.play_song2, state=tk.DISABLED)
        self.play_song2_button.pack()

        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()

        self.matches = []
        self.current_round = 0

    def upload_songs(self):
        """Allow user to upload multiple songs by browsing the file system."""
        file_paths = filedialog.askopenfilenames(
            title="Select Songs",
            filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*"))
        )
        if not file_paths:
            return

        for file_path in file_paths:
            song_name = file_path.split("/")[-1]
            self.songs.append(song_name)
            self.songs_paths.append(file_path)  # Store the file path as well
            self.song_listbox.insert(tk.END, song_name)
            print(f"Uploaded: {song_name} from {file_path}")

    def start_tournament(self):
        if len(self.songs) < 2:
            messagebox.showerror("Error", "At least two songs are required to start the tournament.")
            return
        self.tournament = Bracket(self.songs)  # Create the bracket with uploaded songs
        self.matches = self.tournament.rounds[0]  # Initialize matches with the first round's matches
        self.current_round = 0
        self.show_match()

    def show_match(self):
        """Display the next match in the tournament."""
        if self.current_round < len(self.matches):
            # Get the current match
            match = self.matches[self.current_round]
            
            # Retrieve song names for the match
            song1 = match.competitor_a.name if match.competitor_a else "TBD"
            song2 = match.competitor_b.name if match.competitor_b else "TBD"
            
            # Display the songs
            self.song1_label.config(text=f"Song 1: {song1}")
            self.song2_label.config(text=f"Song 2: {song2}")
            self.vote_button1.config(state=tk.NORMAL)
            self.vote_button2.config(state=tk.NORMAL)
            self.play_song1_button.config(state=tk.NORMAL)
            self.play_song2_button.config(state=tk.NORMAL)

            # Get the file paths for the songs (use the list of file paths)
            song1_path = self.songs_paths[self.songs.index(song1)] if song1 != "TBD" else None
            song2_path = self.songs_paths[self.songs.index(song2)] if song2 != "TBD" else None

            self.current_songs = (song1_path, song2_path)

    def play_song1(self):
        song1_path, _ = self.current_songs
        if song1_path:
            pygame.mixer.music.load(song1_path)
            pygame.mixer.music.play()

    def play_song2(self):
        _, song2_path = self.current_songs
        if song2_path:
            pygame.mixer.music.load(song2_path)
            pygame.mixer.music.play()

    def vote_for_song_1(self):
        """Vote for Song 1 as the winner of the current match."""
        winner_song = self.song1_label.cget("text").split(": ")[1]
        self.update_bracket_after_vote(winner_song)

    def vote_for_song_2(self):
        """Vote for Song 2 as the winner of the current match."""
        winner_song = self.song2_label.cget("text").split(": ")[1]
        self.update_bracket_after_vote(winner_song)

    def update_bracket_after_vote(self, winner_song):
        """Update the bracket after a vote."""
        current_match = self.matches[self.current_round]

        if current_match.competitor_a.name == winner_song:
            current_match.set_winner(current_match.competitor_a)
        elif current_match.competitor_b.name == winner_song:
            current_match.set_winner(current_match.competitor_b)
        else:
            messagebox.showerror("Error", "Invalid vote.")
            return

        # Advance to the next match
        if self.current_round + 1 < len(self.matches):
            self.current_round += 1
            self.show_match()
        else:
            self.prepare_next_round()

    def prepare_next_round(self):
        """Prepare the next round."""
        next_round_matches = self.tournament.advance_to_next_round()
        if not next_round_matches:
            # Tournament is complete, show the winner
            final_match = self.tournament.rounds[-1][0]  # Get the final match
            winner = final_match.get_winner().name if final_match.get_winner() else "TBD"
            messagebox.showinfo("Tournament Winner", f"The winner is: {winner}")
            return

        self.matches = next_round_matches
        self.current_round = 0
        self.show_match()

    def update_bracket(self):
        """Update the bracket visualization after a song wins."""
        self.canvas.delete("all")
        self.draw_bracket()

    def draw_bracket(self):
        """Draw the bracket on the canvas based on current matches."""
        x_spacing = 200
        y_spacing = 60
        y_start = 50

        round_count = len(self.tournament.rounds)

        for round_num in range(round_count):
            matches_in_round = len(self.tournament.rounds[round_num])
            y_offset = y_start + round_num * (y_spacing * matches_in_round)

            for match_idx in range(matches_in_round):
                match = self.tournament.rounds[round_num][match_idx]

                x_offset = 50 + (round_num * x_spacing)

                song1_name = match.competitor_a.name if match.competitor_a else "TBD"
                song2_name = match.competitor_b.name if match.competitor_b else "TBD"
                winner_name = match.get_winner().name if match.get_winner() else "TBD"

                self.canvas.create_text(x_offset, y_offset, text=song1_name, anchor="w", fill="blue")
                self.canvas.create_text(x_offset, y_offset + 20, text=song2_name, anchor="w", fill="red")
                self.canvas.create_text(x_offset + 100, y_offset + 10, text=f"Winner: {winner_name}", anchor="w", fill="green")

                if match_idx < len(self.tournament.rounds[round_num]) - 1:
                    next_x_offset = x_offset + x_spacing
                    next_y_offset = y_start + (y_spacing * (match_idx + 1))
                    self.canvas.create_line(x_offset + 150, y_offset + 10, next_x_offset, next_y_offset, fill="black")

                y_offset += y_spacing


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicTournamentApp(root)
    root.mainloop()
