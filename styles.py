# Dark mode color scheme
DARK_BG = "#2e2e2e"
LIGHT_FG = "#ffffff"
BUTTON_BG = "#ffffff"
BUTTON_FG = "#444444"
HIGHLIGHT_COLOR = "#007acc"
LISTBOX_BG = "#333333"
LISTBOX_FG = "#ffffff"
CANVAS_BG = "#333333"

# Define a function to configure styles
def configure_styles(root):
    from tkinter import ttk

    # Apply dark mode to main window
    root.config(bg=DARK_BG)

    # Apply dark mode to buttons and other widgets
    style = ttk.Style()
    style.configure("TButton", background=BUTTON_BG, foreground=BUTTON_FG, font=("Helvetica", 12), padding=5)
    style.configure("TLabel", background=DARK_BG, foreground=LIGHT_FG, font=("Helvetica", 12))
    style.configure("TFrame", background=DARK_BG)

    # Listbox style
    style.configure("TListbox", background=LISTBOX_BG, foreground=LISTBOX_FG, selectbackground=HIGHLIGHT_COLOR, selectforeground=LIGHT_FG)

    # Canvas style
    style.configure("TCanvas", background=CANVAS_BG)

    return style