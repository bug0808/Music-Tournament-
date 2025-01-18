import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygame
from pytubefix import YouTube
import math
import os
from bracket import Bracket
from match import Match
from competitor import Competitor
from styles import configure_styles
from pydub import AudioSegment



class MusicTournamentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Tournament App")
        
        # Initialize Pygame mixer for audio playback
        pygame.mixer.init()

        # Initialize variables
        self.clashes = []  # List to store Clash objects
        self.winners = []  # Initialize winners as an empty list
        self.songs = []  # List of song names
        self.songs_paths = []  # List of song file paths
        self.tournament = None  # Tournament object to manage rounds
        self.is_paused = False #Tracks if music is paused

        # Apply styles using the imported function
        self.style = configure_styles(self.root)

        # Create a frame for buttons and labels
        self.top_frame = ttk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Create and style Listbox
        self.song_listbox = tk.Listbox(self.top_frame, height=6, selectmode=tk.SINGLE)
        self.song_listbox.grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        # Create buttons with dark mode styles
        self.upload_button = ttk.Button(self.top_frame, text="Upload Song", command=self.upload_songs)
        self.upload_button.grid(row=1, column=0, sticky="w", pady=5)

        self.play_button = ttk.Button(self.top_frame, text="Start Tournament", command=self.start_tournament)
        self.play_button.grid(row=1, column=1, sticky="w", pady=5)

        # Labels for Song 1 and Song 2
        self.song1_label = ttk.Label(self.top_frame, text="Song 1: TBD")
        self.song1_label.grid(row=2, column=0, sticky="w")

        self.song2_label = ttk.Label(self.top_frame, text="Song 2: TBD")
        self.song2_label.grid(row=2, column=1, sticky="w")

        # Vote buttons with dark mode styles
        self.vote_button1 = ttk.Button(self.top_frame, text="Vote for Song 1", command=self.vote_for_song_1, state=tk.DISABLED)
        self.vote_button1.grid(row=3, column=0, pady=5)

        self.vote_button2 = ttk.Button(self.top_frame, text="Vote for Song 2", command=self.vote_for_song_2, state=tk.DISABLED)
        self.vote_button2.grid(row=3, column=1, pady=5)

        # Play Song buttons with dark mode styles
        self.play_song1_button = ttk.Button(self.top_frame, text="Play Song 1", command=self.play_song1, state=tk.NORMAL)
        self.play_song1_button.grid(row=4, column=0, pady=5)

        self.play_song2_button = ttk.Button(self.top_frame, text="Play Song 2", command=self.play_song2, state=tk.NORMAL)
        self.play_song2_button.grid(row=4, column=1, pady=5)

        self.volume_label = ttk.Label(self.top_frame, text="Volume:")
        self.volume_label.grid(row=5, column=0, sticky="w", pady=5)

        self.volume_slider = tk.Scale(self.top_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.adjust_volume)
        self.volume_slider.set(50)  # Set initial volume to 50%
        self.volume_slider.grid(row=5, column=1, pady=5)

        # New YouTube URL entry and download button
        self.youtube_label = ttk.Label(self.top_frame, text="YouTube URL:")
        self.youtube_label.grid(row=6, column=0, sticky="w", pady=5)

        self.youtube_entry = ttk.Entry(self.top_frame, width=40)
        self.youtube_entry.grid(row=6, column=1, pady=5)

        self.youtube_button = ttk.Button(self.top_frame, text="Add YouTube Song", command=self.add_youtube_song)
        self.youtube_button.grid(row=7, column=0, columnspan=2, pady=5)


        # Create control buttons
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.TOP, pady=10)

        self.stop_button = ttk.Button(control_frame, text="Stop Song", command=self.stop_song)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = ttk.Button(control_frame, text="Pause Song", command=self.pause_song)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.resume_button = ttk.Button(control_frame, text="Resume Song", command=self.resume_song)
        self.resume_button.pack(side=tk.LEFT, padx=5)

        # Create a frame for the canvas (bracket visualization)
        self.bracket_frame = ttk.Frame(root)
        self.bracket_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add scrollbars for the canvas
        self.h_scrollbar = tk.Scrollbar(self.bracket_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.v_scrollbar = tk.Scrollbar(self.bracket_frame, orient=tk.VERTICAL)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Style and create the canvas
        self.canvas = tk.Canvas(self.bracket_frame, width=800, height=600, scrollregion=(0,0,2000,2000))
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.config(bg="mediumpurple1")
        
        self.canvas.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        self.h_scrollbar.config(command=self.canvas.xview)
        self.v_scrollbar.config(command=self.canvas.yview)

        # Initialize matches and current round
        self.matches = []
        self.current_round = 0

    
    def add_youtube_song(self):
        """Download audio from a YouTube URL and add it as a song."""
        url = self.youtube_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return

        try:
            yt = YouTube(url)
            audio_stream = yt.streams.filter(only_audio=True).first()

            if not audio_stream:
                messagebox.showerror("Error", "No audio streams found for this video.")
                return

            output_dir = "downloads"
            os.makedirs(output_dir, exist_ok=True)

            # Download the audio
            file_path = audio_stream.download(output_dir)
            new_file_path = os.path.splitext(file_path)[0] + ".mp3"
            print(new_file_path)
            # Convert to .mp3 if necessary
            if not file_path.endswith(".mp3"):
                os.rename(file_path, new_file_path)
            
            # Re-encode the MP3 file
            print(f"File path after download: {file_path}")
            print(f"File path after renaming to MP3: {new_file_path}")
            print(f"File exists: {os.path.exists(new_file_path)}")
            fixed_file_path = self.reencode_mp3(new_file_path)
            if fixed_file_path:
                new_file_path = fixed_file_path

            # Avoid duplicates
            song_name = yt.title
            if song_name in self.songs:
                messagebox.showwarning("Duplicate Song", f"{song_name} is already in the list.")
                return

            # Append the song and path
            self.songs.append(song_name)
            self.songs_paths.append(new_file_path)
            self.song_listbox.insert(tk.END, song_name)

            messagebox.showinfo("Success", f"Downloaded and added: {song_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download from YouTube: {e}")
    
    #move to its own file later
    def reencode_mp3(self, file_path):
        try:
            audio = AudioSegment.from_file(file_path)
            
            audio.export(file_path, format="mp3")
            return file_path
        except Exception as e:
            messagebox.showerror("Error", f"Failed to re-encode the file: {e}")
            return None

    def upload_songs(self):
        """Allow user to upload multiple songs by browsing the file system."""
        file_paths = filedialog.askopenfilenames(
            title="Select Songs",
            filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*"))
        )
        if not file_paths:
            return

        for file_path in file_paths:
            song_name = os.path.splitext(file_path.split("/")[-1])[0]  # Remove .mp3 extension
            self.songs.append(song_name)
            self.songs_paths.append(file_path)  # Store the file path as well
            self.song_listbox.insert(tk.END, song_name)
            print(f"Uploaded: {song_name} from {file_path}")
            
    def adjust_volume(self, volume):
        """Adjust the volume of the music."""
        volume = int(volume) / 100  # Convert to a range between 0 and 1
        pygame.mixer.music.set_volume(volume)


    def stop_song(self):
        """Stop the currently playing song."""
        pygame.mixer.music.stop()
        self.is_paused = False

    def pause_song(self):
        """Pause the currently playing song."""
        if not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True

    def resume_song(self):
        """Resume the currently paused song."""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False


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
            self.vote_button1.config(text=f"Vote for {song1}",state=tk.NORMAL)
            self.vote_button2.config(text=f"Vote for {song2}",state=tk.NORMAL)
            self.play_song1_button.config(state=tk.NORMAL)
            self.play_song2_button.config(state=tk.NORMAL)

            # Get the file paths for the songs (use the list of file paths)
            song1_path = self.songs_paths[self.songs.index(song1)] if song1 != "TBD" else None
            song2_path = self.songs_paths[self.songs.index(song2)] if song2 != "TBD" else None

            self.current_songs = (song1_path, song2_path)

    def play_song1(self):
        song1_path, _ = self.current_songs
        if song1_path and os.path.exists(song1_path):  # Ensure file exists
            pygame.mixer.music.load(song1_path)
            pygame.mixer.music.play()
        else:
            messagebox.showerror("Error", "Song file not found!")

    def play_song2(self):
        _, song2_path = self.current_songs
        if song2_path and os.path.exists(song2_path):  # Ensure file exists
            pygame.mixer.music.load(song2_path)
            pygame.mixer.music.play()
        else:
            messagebox.showerror("Error", "Song file not found!")


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

        # Calculate the canvas scrollregion dynamically
        max_x = start_x + round_spacing * len(self.tournament.rounds)
        max_y = start_y + match_spacing * max(len(round_matches) for round_matches in self.tournament.rounds)
        self.canvas.config(scrollregion=(0, 0, max_x + 100, max_y + 100))


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
                    self.canvas.create_text(x + box_width + 20, y + box_height // 2 + 10, text=f"Winner: {winner_name}", anchor="w", fill="gold")

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicTournamentApp(root)
    root.mainloop()
