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

        # Create a frame for buttons and labels
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.song_listbox = tk.Listbox(self.top_frame, height=6)
        self.song_listbox.grid(row=0, column=0, columnspan=2, sticky="w")

        self.upload_button = tk.Button(self.top_frame, text="Upload Song", command=self.upload_songs)
        self.upload_button.grid(row=1, column=0, sticky="w", pady=5)

        self.play_button = tk.Button(self.top_frame, text="Start Tournament", command=self.start_tournament)
        self.play_button.grid(row=1, column=1, sticky="w", pady=5)

        self.song1_label = tk.Label(self.top_frame, text="Song 1: TBD")
        self.song1_label.grid(row=2, column=0, sticky="w")

        self.song2_label = tk.Label(self.top_frame, text="Song 2: TBD")
        self.song2_label.grid(row=2, column=1, sticky="w")

        self.vote_button1 = tk.Button(self.top_frame, text="Vote for Song 1", command=self.vote_for_song_1, state=tk.DISABLED)
        self.vote_button1.grid(row=3, column=0, pady=5)

        self.vote_button2 = tk.Button(self.top_frame, text="Vote for Song 2", command=self.vote_for_song_2, state=tk.DISABLED)
        self.vote_button2.grid(row=3, column=1, pady=5)

        self.play_song1_button = tk.Button(self.top_frame, text="Play Song 1", command=self.play_song1, state=tk.NORMAL)
        self.play_song1_button.grid(row=4, column=0, pady=5)

        self.play_song2_button = tk.Button(self.top_frame, text="Play Song 2", command=self.play_song2, state=tk.NORMAL)
        self.play_song2_button.grid(row=4, column=1, pady=5)

        # self.stop_button = tk.Button(self.top_frame, text="Stop Audio", command=self.stop_audio, state=tk.NORMAL)
        # self.stop_button.grid(row=5, column=0, pady=5)


        # Create a frame for the canvas (bracket visualization)
        self.bracket_frame = tk.Frame(root)
        self.bracket_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.bracket_frame, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

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
        self.update_ui()  # Call the centralized UI update
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
            self.update_ui()  # Update UI after a vote
            self.prepare_next_round()

    def prepare_next_round(self):
        """Prepare the next round."""
        next_round_matches = self.tournament.advance_to_next_round()
        if not next_round_matches:
            # Tournament is complete, show the winner
            final_match = self.tournament.rounds[-1][0]  # Get the final match
            winner = final_match.get_winner().name if final_match.get_winner() else "TBD"
            messagebox.showinfo("Tournament Winner", f"The winner is: {winner}")
            self.update_ui()  # Update UI after a vote
            return
        
        self.update_ui()  # Update UI after a vote
        self.matches = next_round_matches
        self.current_round = 0
        self.show_match()

    def update_bracket(self):
        """Update the bracket visualization after a song wins."""
        self.canvas.delete("all")
        self.draw_bracket()

    def update_ui(self):
        self.show_match()  # Show the current match
        self.draw_bracket()  # Redraw the bracket

    def draw_bracket(self):
        """Draw the bracket on the canvas based on the current tournament state."""
        print("Drawing the bracket...")  # Debugging statement
        self.canvas.delete("all")  # Clear the canvas

        if not self.tournament:
            return

        # Constants for drawing
        round_spacing = 200  # Space between rounds
        match_spacing = 80   # Space between matches within a round
        box_width = 150      # Width of each match box
        box_height = 30      # Height of each match box
        start_x = 50         # Starting x-coordinate for the first round
        start_y = 50         # Starting y-coordinate

        for round_idx, round_matches in enumerate(self.tournament.rounds):
            x = start_x + round_idx * round_spacing  # X-coordinate for the current round

            for match_idx, match in enumerate(round_matches):
                # Calculate the y-coordinate for this match
                y = start_y + match_idx * match_spacing

                # Get competitors' names
                competitor_a_name = match.competitor_a.name if match.competitor_a else "TBD"
                competitor_b_name = match.competitor_b.name if match.competitor_b else "TBD"
                winner_name = match.get_winner().name if match.get_winner() else "TBD"

                # Draw boxes for the competitors
                self.canvas.create_rectangle(x, y, x + box_width, y + box_height, outline="black", fill="lightblue")
                self.canvas.create_text(x + 5, y + box_height // 2, text=competitor_a_name, anchor="w")

                self.canvas.create_rectangle(x, y + box_height + 10, x + box_width, y + 2 * box_height + 10, outline="black", fill="lightcoral")
                self.canvas.create_text(x + 5, y + box_height + 10 + box_height // 2, text=competitor_b_name, anchor="w")

                # If this is not the last round, draw lines to the next round
                if round_idx + 1 < len(self.tournament.rounds):
                    next_x = x + round_spacing
                    next_match_idx = match_idx // 2
                    next_y = start_y + next_match_idx * match_spacing + box_height // 2
                    mid_y = y + box_height + 5  # Midpoint of the current match

                    # Draw connecting lines
                    self.canvas.create_line(x + box_width, mid_y, next_x, next_y, fill="black")
                    self.canvas.create_line(x + box_width, mid_y + box_height, next_x, next_y, fill="black")

                # Draw winner information
                if round_idx + 1 == len(self.tournament.rounds):  # If this is the last round
                    self.canvas.create_text(x + box_width + 20, y + box_height // 2 + 10, text=f"Winner: {winner_name}", anchor="w", fill="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicTournamentApp(root)
    root.mainloop()
