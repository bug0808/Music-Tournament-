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
        self.rounds = []  # List to store rounds
        self.current_round = 0  # Initialize current round
        self.generate_bracket()

    def generate_bracket(self):
        """Generate the bracket structure from the list of competitors."""
        rounds = []
        competitors = [Competitor(name, "") for name in self.competitors]  # Create Competitor objects

        # Ensure the number of competitors is a power of 2
        next_power_of_2 = 2 ** math.ceil(math.log2(len(competitors)))
        while len(competitors) < next_power_of_2:
            competitors.append(Competitor("TBD", ""))  # Add "TBD" as a Competitor object

        # Create matches for the first round
        round_matches = []
        for i in range(0, len(competitors), 2):
            round_matches.append(Match(competitors[i], competitors[i+1]))
        rounds.append(round_matches)

        # Create subsequent rounds based on winners from previous rounds
        while len(rounds[-1]) > 1:
            next_round_matches = []
            for i in range(0, len(rounds[-1]), 2):
                next_round_matches.append(Match(rounds[-1][i].winner, rounds[-1][i+1].winner))
            rounds.append(next_round_matches)

        self.rounds = rounds

    def get_current_round_matches(self):
        """Return the list of matches for the current round."""
        return self.rounds[self.current_round]

    def next_round(self):
        """Advance to the next round."""
        self.current_round += 1




class MusicTournamentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Tournament App")
        self.clashes = []  # List to store Clash objects
        pygame.mixer.init()  # Initialize Pygame mixer for audio playback

        self.songs = []  # List of song names
        self.songs_paths = []  # List of song file paths
        self.tournament = None  # Tournament object to manage rounds
        self.song_listbox = tk.Listbox(root)
        self.song_listbox.pack()

        self.upload_button = tk.Button(root, text="Upload Song", command=self.upload_song)
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

        self.swap_button = tk.Button(root, text="Swap Songs", command=self.swap_songs, state=tk.DISABLED)
        self.swap_button.pack()

        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()

        self.matches = []
        self.current_round = 0

    def upload_song(self):
        """Allow user to upload a song by browsing the file system."""
        file_path = filedialog.askopenfilename(
            title="Select a Song",
            filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*"))
        )
        if not file_path:
            return

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
            self.swap_button.config(state=tk.NORMAL)

            # Get the file paths for the songs (use the list of file paths)
            song1_path = self.songs_paths[self.songs.index(song1)] if song1 != "TBD" else None
            song2_path = self.songs_paths[self.songs.index(song2)] if song2 != "TBD" else None

            if song1_path and song2_path:
                self.play_song(song1_path, song2_path)  # Pass the paths of the songs

    
    def play_song(self, song1_path, song2_path):
        """Play the selected song."""
        # Check if song paths are valid
        if not song1_path or not song2_path:
            print("Error: Invalid song paths")
            return

        # Run the play function in a separate thread
        threading.Thread(target=self.play, args=(song1_path, song2_path), daemon=True).start()

    def play(self, song1_path, song2_path):
        """Helper function to play the songs in sequence."""
        # Load and play Song 1
        if song1_path:
            pygame.mixer.music.load(song1_path)
            pygame.mixer.music.play()
            # Wait until the song finishes
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

        # Load and play Song 2
        if song2_path:
            pygame.mixer.music.load(song2_path)
            pygame.mixer.music.play()
            # Wait until the song finishes
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

    def swap_songs(self):
        """Swap between the two playing songs."""
        pass  # TODO: Implement functionality to swap songs.

    def vote_for_song_1(self):
        """Vote for Song 1 as the winner of the current match."""
        winner_song = self.song1_label.cget("text").split(": ")[1]
        self.update_bracket_after_vote(winner_song)

    def vote_for_song_2(self):
        """Vote for Song 2 as the winner of the current match."""
        winner_song = self.song2_label.cget("text").split(": ")[1]
        self.update_bracket_after_vote(winner_song)

    def update_bracket_after_vote(self, winner_song):
        """Update the bracket after a vote and redraw the visualization."""
        current_match = self.matches[self.current_round]

        # Ensure that competitors exist
        if current_match.competitor_a and current_match.competitor_b:
            # Set the winner in the current match
            if current_match.competitor_a.name == winner_song:
                current_match.set_winner(current_match.competitor_a)
            elif current_match.competitor_b.name == winner_song:
                current_match.set_winner(current_match.competitor_b)
        else:
            messagebox.showerror("Error", "One or both competitors are not properly initialized.")
            return

        # Advance to the next round
        if self.current_round + 1 < len(self.matches):
            self.current_round += 1
            self.show_match()
        else:
            # Move to the next round of matches
            self.tournament.next_round()  # Advance to the next round in the bracket
            self.matches = self.tournament.get_current_round_matches()

            # If no more rounds, declare the winner
            if not self.matches:
                # Assuming the final match is the last match in the bracket
                final_match = self.matches[-1] if self.matches else None
                if final_match and final_match.competitor_a and final_match.competitor_b:
                    winner = final_match.get_winner()
                    messagebox.showinfo("Tournament Over", f"The winner is {winner.name}!")
                else:
                    messagebox.showinfo("Tournament Over", "The final match is incomplete.")
                self.root.quit()
            else:
                self.current_round = 0  # Reset to first match in the new round
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
