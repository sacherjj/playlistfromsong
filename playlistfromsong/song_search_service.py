import requests
from lxml import html
from urllib.parse import unquote
from collections import namedtuple


class SongSearchService(object):
    def get_songs(self, search_string, limit=None):
        raise NotImplementedError


LastFMLink = namedtuple('LastFMLink', 'artist song url')


class TuneFM(SongSearchService):

    NUMBER_LINKS = 10

    def __init__(self):
        self.used_links = set()

    @staticmethod
    def _parse_artist_song(url):
        url_parts = url.split('/')
        if len(url_parts) < 6:
            return None
        artist_name = unquote(url_parts[4]).replace('+', ' ')
        song_name = unquote(url_parts[-1]).replace('+', ' ')
        return LastFMLink(artist_name, song_name, url)

    @staticmethod
    def _process_lastfm_link(url):
        r = requests.get(url)
        tree = html.fromstring(r.content)
        youtube_section = tree.xpath('//div[@class="video-preview"]')
        youtube_url = None
        if len(youtube_section) > 0:
            possible_youtubes = youtube_section[0].xpath('//a[@target="_blank"]')
            for possible_youtube in possible_youtubes:
                if 'href' in possible_youtube.attrib:
                    if 'youtube.com' in possible_youtube.attrib['href']:
                        youtube_url = possible_youtube.attrib['href']
                        break

        if not youtube_url:
            return None

        lastfm_tracks = []
        sections = tree.xpath('//section[@class="grid-items-section"]')
        if sections:
            for track in sections[0].findall('.//a'):
                lastfm_tracks.append('https://www.last.fm' + track.attrib['href'])
        return youtube_url, lastfm_tracks

    def get_songs(self, search_string, limit=None):
        current_url = self.get_initial_url(search_string)
        lastfm_links = []
        yield_count = 0
        while current_url:
            data = self.get_youtube_and_links_from_url(current_url)
            current_url = None
            if data:
                youtube_url, lastfm_link, full_links = data
                lastfm_links.extend(set([link.url for link in full_links]) - self.used_links)
                yield youtube_url, lastfm_link
                yield_count += 1
                try:
                    current_url = lastfm_links.pop()
                except IndexError:
                    current_url = None
            if limit and yield_count >= limit:
                current_url = None

    def get_youtube_and_links_from_url(self, lastfm_url):
        if lastfm_url not in self.used_links:
            self.used_links.add(lastfm_url)
            lastfm_link = self._parse_artist_song(lastfm_url)
            if lastfm_link:
                artist_name, song_name, url = lastfm_link
                results = self._process_lastfm_link(lastfm_url)
                if results:
                    youtube_url, lastfm_links = results
                    unused_links = list(set(lastfm_links) - self.used_links)
                    # Get full data for display, but limit list to NUMBER_LINKS length
                    unused_links = [self._parse_artist_song(url) for url in unused_links[:self.NUMBER_LINKS]]
                    return youtube_url, lastfm_link, unused_links

    @staticmethod
    def get_initial_url(search_string):
        r = requests.get('https://www.last.fm/search?', {'q': search_string})
        tree = html.fromstring(r.content)
        possible_tracks = tree.xpath('//span/a[@class="link-block-target"]')
        for i, track in enumerate(possible_tracks):
            return 'https://www.last.fm' + track.attrib['href']
        return None


class Spotify(SongSearchService):
    def __init__(self, token):
        self.token = token

    def get_songs(self, search_string, limit=None):
        raise NotImplementedError


if __name__ == '__main__':
    tfm = TuneFM()
    url = tfm.get_initial_url('John Williams')
    youtube_link, lastfm, related = tfm.get_youtube_and_links_from_url(url)
    print(youtube_link, lastfm, related)

    for song in tfm.get_songs('John Williams Superman', 10):
        print(song)

