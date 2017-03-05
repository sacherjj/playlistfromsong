import requests
from lxml import html
from urllib.parse import unquote


class SongSearchService(object):
    def get_songs(self, search_string):
        raise NotImplementedError


class TuneFM(SongSearchService):
    @staticmethod
    def _get_first_lastfm_url(search_string):
        r = requests.get('https://www.last.fm/search?', {'q': search_string})
        tree = html.fromstring(r.content)
        possible_tracks = tree.xpath('//span/a[@class="link-block-target"]')
        for i, track in enumerate(possible_tracks):
            return 'https://www.last.fm' + track.attrib['href']
        return ""

    @staticmethod
    def _parse_artist_song(url):
        url_parts = url.split('/')
        if len(url_parts) < 6:
            return None
        artist_name = unquote(url_parts[4]).replace('+', ' ')
        song_name = unquote(url_parts[-1]).replace('+', ' ')
        return artist_name, song_name

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

    def get_songs(self, search_string):
        current_url = self._get_first_lastfm_url(search_string)
        lastfm_links = [current_url]

        used_links = set()
        while lastfm_links:
            current_url = lastfm_links.pop()
            if current_url not in used_links:
                used_links.add(current_url)
                artist_song = self._parse_artist_song(current_url)
                if artist_song:
                    artist_name, song_name = artist_song
                    results = self._process_lastfm_link(current_url)
                    if results:
                        youtube_url, new_lastfm_links = results
                        lastfm_links.extend(set(new_lastfm_links)-used_links)
                        yield youtube_url, artist_name, song_name


class Spotify(SongSearchService):
    def __init__(self, token):
        self.token = token

    def get_songs(self, search_string):
        pass


if __name__ == '__main__':
    tfm = TuneFM()
    for song in tfm.get_songs('Every Rose'):
        print(song)
