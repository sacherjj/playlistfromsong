import sys, os
import subprocess
from collections import deque
import inspect
import time


def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False):  # py2exe, PyInstaller, cx_Freeze
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
        script_dir = get_script_dir()
        save_dir = os.path.join(script_dir, 'songs')
        print('Script Dir: {}'.format(script_dir))
        print('Saving to: {}'.format(save_dir))
        os.chdir(save_dir)
        self._options = ['--extract-audio',
                         '--prefer-ffmpeg',
                         '--audio-format mp3',
                         '--ffmpeg {}'.format(script_dir),
                         '--audio-quality {}'.format(quality)]
        if rate_limit:
            self._options.append('--limit-rate {}'.format(rate_limit))

        self._queue = deque()
        self._process = None
        self.work_left = False

    @property
    def queue_count(self):
        # Always one more in queue, to account for current one.
        return len(self._queue)

    def add_to_queue(self, url):
        self._queue.append(url)
        self.work_left = True
        if not self._process:
            self.process_queue()

    def _save_process_details(self, stdout=None, stderr=None, both=None):
        err_output = []
        std_output = []
        if both:
            err_output.append(both)
            std_output.append(both)
        if stdout:
            std_output.append(stdout)
        if stderr:
            err_output.append(stderr)
        if std_output:
            with open(os.path.join(get_script_dir(), 'out.txt'), 'w') as f:
                for entry in std_output:
                    f.write(entry)
        if err_output:
            with open(os.path.join(get_script_dir(), 'err.txt'), 'w') as f:
                for entry in err_output:
                    f.write(entry)

    def process_queue(self):
        if self._process:
            self._process.poll()
            # When done, code will be int.
#            out_values = self._process.stdout.read().decode('UTF-8')
#            err_values = self._process.stderr.read().decode('UTF-8')
#            self._save_process_details(stderr=err_values)
            if self._process.returncode is not None:
                self._process = None
        else:
            if self._queue:
                url = self._queue.pop()
#                self._save_process_details(both='---')
                self.download_audio(url, self._options)
            else:
                self.work_left = False

    def download_audio(self, url, arguments):
        if len(url) == 0:
            return
        suffix = ''
        if sys.platform.startswith('win'):
            suffix = '.exe'
        # Used to get output and subprocess to work with PyInstaller
        out_path = os.path.join(get_script_dir(), 'out.txt')
        with open(out_path, 'w') as f:
            try:
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                command = "youtube-dl{} {} {}".format(suffix, ' '.join(arguments), url)
                self._process = subprocess.Popen(command.split(),
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
            except OSError as e:
                f.write('Failed: ' + str(e))



if __name__ == '__main__':
    ytd = YoutubeDownloader(2, '2M')
    ytd.add_to_queue('https://www.youtube.com/watch?v=tPEE9ZwTmy0')
    ytd.add_to_queue('https://www.youtube.com/watch?v=a3HZ8S2H-GQ')
    while ytd.work_left:
        ytd.process_queue()
        time.sleep(0.5)
    ytd.add_to_queue('https://www.youtube.com/watch?v=oiWWKumrLH8')
    while ytd.work_left:
        ytd.process_queue()
        time.sleep(0.5)

