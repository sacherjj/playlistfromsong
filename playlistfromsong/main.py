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
        self.pending_links = None  # Holds links of current choice.  Included if Accepted.
        self.future_data = None  # Holds prefetched data.
        self.after(1000, self.update)

    def update(self):
        if self.downloader.work_left:
            count = self.downloader.queue_count + 1
            self.status_bar.text = 'Downloading...  {} left.'.format(count)
            self.downloader.process_queue()
        else:
            self.status_bar.text = ''
        self.after(1000, self.update)

    def reject_song(self):
        self.next_song()

    def extend_links(self):
        if self.pending_links:
            self.links.extend(list(set(self.pending_links) - set(self.links)))
            self.pending_links = None

    def accept_song(self):
        self.extend_links()
        self.downloader.add_to_queue(self.youtube)
        self.next_song()

    def prefetch(self):
        if self.links:
            self.future_data = self.search_service.get_youtube_and_links_from_url(self.links[0].url)
        self.song_frame.set_button_state('normal')

    def next_song(self):
        self.song_frame.set_button_state('disabled')
        self.song_frame.clear_data()
        new_data = None
        while self.links and not new_data:
            next_song = self.links.popleft()
            if self.future_data:
                new_data = self.future_data
                self.future_data = None
            else:
                new_data = self.search_service.get_youtube_and_links_from_url(next_song.url)
        if new_data:
            self.youtube, self.current_link, self.pending_links = new_data
            if len(self.links) < 2:
                self.extend_links()
            self.song_frame.load_songs(self.current_link, self.links)
            self.after(10, self.prefetch)
        else:
            self.status_bar.text = 'Nothing Found.'

    def do_search(self):
        self.song_frame.set_button_state('disabled')
        self.search_button['state'] = 'disabled'
        self.song_frame.clear_data()
        self.links.clear()
        self.future_data = None
        self.status_bar.text = 'Searching...'
        self.after(10, self.async_search)

    def async_search(self):
        value = self.search_var.get()
        link_data = self.search_service.get_initial_url(value)
        if link_data:
            self.links.append(link_data)
            self.next_song()
        else:
            self.status_bar.text = 'Nothing Found.'
        self.search_button['state'] = 'normal'


if __name__ == '__main__':
    mw = MainWindow()
    mw.mainloop()
