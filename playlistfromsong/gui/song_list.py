import tkinter as tk
from playlistfromsong.gui.images import ImageButton


class SongList(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super().__init__(parent, *args, **kwargs)
        self._artist_vars = []
        self._song_vars = []
        self._setup_grid()

    def _setup_grid(self):
        tk.Label(self, text='Artist Name', anchor=tk.W).grid(row=0, column=0, sticky=tk.EW)
        tk.Label(self, text='Song Name', anchor=tk.W).grid(row=0, column=1, sticky=tk.EW)
        tk.Label(self, text='Accept').grid(row=0, column=2)
        tk.Label(self, text='Reject').grid(row=0, column=3)

        self.main_artist = tk.StringVar()
        tk.Label(self, textvariable=self.main_artist, anchor=tk.W).grid(row=1, column=0, sticky=tk.EW)
        self.main_song = tk.StringVar()
        tk.Label(self, textvariable=self.main_song, anchor=tk.W).grid(row=1, column=1, sticky=tk.EW)

        self.accept_button = ImageButton(self, 'check', self.accept)
        self.accept_button.grid(row=1, column=2)

        self.reject_button = ImageButton(self, 'x', self.rejected)
        self.reject_button.grid(row=1, column=3)

        self.set_button_state('disabled')

        tk.Label(self, text='Releated Songs:', anchor=tk.W).grid(row=2, column=0, columnspan=2, sticky=tk.EW)

        for row_number in range(3, 18):
            self._setup_row(row_number)

        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(2, weight=2)

    def _setup_row(self, row_number):
        artist = tk.StringVar()
        tk.Label(self, textvariable=artist, anchor=tk.W).grid(row=row_number, column=0, sticky=tk.EW)

        self._artist_vars.append(artist)

        song = tk.StringVar()
        tk.Label(self, textvariable=song, anchor=tk.W).grid(row=row_number, column=1, sticky=tk.EW)
        self._song_vars.append(song)

    def clear_data(self):
        self.main_artist.set('')
        self.main_song.set('')
        for artist_var in self._artist_vars:
            artist_var.set('')
        for song_var in self._song_vars:
            song_var.set('')

    def load_songs(self, current_link, links):
        self.main_artist.set(current_link.artist)
        self.main_song.set(current_link.song)
        for i, link in enumerate(links):
            if i < len(self._artist_vars):
                self._artist_vars[i].set(link.artist)
                self._song_vars[i].set(link.song)

    def set_button_state(self, state):
        self.accept_button['state'] = state
        self.reject_button['state'] = state

    def accept(self):
        self.parent.accept_song()

    def rejected(self):
        self.parent.reject_song()