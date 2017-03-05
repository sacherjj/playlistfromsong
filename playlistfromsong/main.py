import tkinter as tk
from collections import deque
from playlistfromsong.gui.status_bar import StatusBar
from playlistfromsong.song_search_service import TuneFM
from playlistfromsong.gui.song_list import SongList
from playlistfromsong.youtube_downloader import YoutubeDownloader
# For PyInstaller
import queue


class MainWindow(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Song Search and Downloader')

        self.status_bar = StatusBar(self)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.top_frame = tk.Frame()
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.search_label = tk.Label(self.top_frame, text="Search Text:")
        self.search_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.top_frame, textvariable=self.search_var, width=80)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.search_button = tk.Button(self.top_frame, command=self.do_search, text="Search")
        self.search_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.song_frame = SongList(self)
        self.song_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.search_service = TuneFM()
        self.downloader = YoutubeDownloader(3, '4M')

        self.youtube = ''
        self.current_link = None
        self.links = deque()
        self.after(1000, self.update)

    def update(self):
        if self.downloader.work_left:
            count = self.downloader.queue_count + 1
            self.status_bar.text = 'Downloading {}...'.format(count)
            self.downloader.process_queue()
        else:
            self.status_bar.text = ''
        self.after(1000, self.update)

    def reject_song(self):
        self.next_song()

    def accept_song(self):
        self.downloader.add_to_queue(self.youtube)
        self.next_song()

    def next_song(self):
        self.song_frame.clear_data()
        new_data = None
        while self.links and not new_data:
            next_song = self.links.popleft()
            new_data = self.search_service.get_youtube_and_links_from_url(next_song.url)
        if new_data:
            self.youtube, self.current_link, new_links = new_data
            self.links.extend(list(set(new_links)-set(self.links)))
            self.song_frame.load_songs(self.current_link, self.links)

    def do_search(self):
        self.song_frame.clear_data()
        self.links.clear()
        value = self.search_var.get()
        initial_url = self.search_service.get_initial_url(value)
        if initial_url:
            tunefm_data = self.search_service.get_youtube_and_links_from_url(initial_url)
            if tunefm_data:
                self.youtube, self.current_link, links = tunefm_data
                self.links.extend(links)
                self.song_frame.load_songs(self.current_link, self.links)
                return
        self.status_bar.set_timed_text('Nothing Found.', 5000)

if __name__ == '__main__':
    mw = MainWindow()
    mw.mainloop()
