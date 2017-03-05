import sys, os
import subprocess
from collections import deque
import inspect
import time


def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


class YoutubeDownloader(object):
    """
    Downloads youtube videos one at a time, but queues up videos to download.

    Allows download rate limiting.
    """
    def __init__(self, quality=3, rate_limit=None,):
        os.chdir(os.path.join(get_script_dir(), 'songs'))
        self._options = ['--extract-audio',
                         '--audio-format mp3',
                         '--ffmpeg {}'.format(get_script_dir()),
                         '--audio-quality {}'.format(quality)]
        if rate_limit:
            self._options.append('--limit-rate {}'.format(rate_limit))

        self._queue = deque()
        self._process = None
        self.work_left = False

    @property
    def queue_count(self):
        # Always one more in queue, to account for current one.
        return len(self._queue) + 1


    def add_to_queue(self, url):
        self._queue.append(url)
        self.work_left = True
        if not self._process:
            self._process_queue()

    def _process_queue(self):
        if self._process:
            self._process.poll()
            print(self._process.returncode)
            # When done, code will be int.
            if self._process.returncode is None:
                self._process = None
        else:
            if self._queue:
                url = self._queue.pop()
                self.download_audio(url, self._options)
            else:
                self.work_left = False

    def download_audio(self, url, arguments):
        if len(url) == 0:
            return
        suffix = ''
        if sys.platform.startswith('win'):
            suffix = '.exe'

        command = "youtube-dl{} {} {}".format(suffix, ' '.join(arguments), url)
        self._process = subprocess.Popen(command.split(),
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)


if __name__ == '__main__':
    ytd = YoutubeDownloader(2, '2M')
    ytd.add_to_queue('https://www.youtube.com/watch?v=tPEE9ZwTmy0')
    ytd.add_to_queue('https://www.youtube.com/watch?v=a3HZ8S2H-GQ')
    while ytd.work_left:
        ytd._process_queue()
        time.sleep(0.5)
    ytd.add_to_queue('https://www.youtube.com/watch?v=oiWWKumrLH8')
    while ytd.work_left:
        ytd._process_queue()
        time.sleep(0.5)

