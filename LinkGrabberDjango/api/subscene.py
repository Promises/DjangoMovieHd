"""
Python wrapper for Subscene subtitle database.
since Subscene doesn't provide an official API, I wrote
this script that does the job by parsing the website"s pages.
"""

# imports
import re

import cchardet
import enum

import requests
from bs4 import BeautifulSoup

# constants
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
}
SITE_DOMAIN = "https://subscene.com"
COOKIES = {
 "trc_cookie_storage" : "taboola%2520global%253Auser-id%3Dec4ccc14-eb37-4167-b8e9-940401d55a96-tuct52e02c",
 "_gat" : "1",
 "_ga":"GA1.2.2123271073.1499028138",
 "_gid":"GA1.2.262418581.1500222757",
}


# utils
def soup_for(url):
    url = re.sub("\s", "+", url)
    r = requests.get(url, headers=HEADERS, cookies=COOKIES)
    html = r.content
    return BeautifulSoup(html, "html.parser")


class AttrDict():
    to_dict = lambda self: {k: getattr(self, k) for k in self._attrs}

    def __init__(self, *attrs):
        self._attrs = attrs

        for attr in attrs:
            setattr(self, attr, "")


# models
@enum.unique
class SearchTypes(enum.Enum):
    Exact = 1
    TvSerie = 2
    Popular = 3
    Close = 4


SectionsParts = {
    SearchTypes.Exact: "Exact",
    SearchTypes.TvSerie: "TV-Series",
    SearchTypes.Popular: "Popular",
    SearchTypes.Close: "Close"
}


class Subtitle:
    def __init__(self, title, url, language, description):
        self.title = title
        self.url = url
        self.language = language
        self.description = description

    def __str__(self):
        return self.title

    @classmethod
    def from_rows(cls, rows):
        subtitles = []

        for row in rows:
            if row.td.a is not None:
                if row.td.a.span.findAll(text=re.compile(r'English')):
                    if not row.td.a.findAll(text=re.compile(r'railer')):
                        subtitles.append(cls.from_row(row))

        l = [i for i in subtitles if i is not None]
        return l

    @classmethod
    def from_row(cls, row):
        pattern = re.compile(r'English')
        if row.find(text=pattern):

            attrs = AttrDict("title", "url", "language", "description")

            attrs.title = row.find("td", "a1").a.find_all("span")[1].text.strip()

            attrs.url = SITE_DOMAIN + row.find("td", "a1").a.get("href")

            attrs.language = row.find("td", "a1").a.find_all("span")[0].text.strip()

            attrs.description = row.find("td", "a6").div.text.strip()

            return cls(**attrs.to_dict())
        else:
            return



def zipped_url(self):
    soup = soup_for(self.url)
    return SITE_DOMAIN + soup.find("div", "download").a.get("href")


class Film:
    def __init__(self, title, year=None, imdb=None, cover=None, subtitles=None):
        self.title = title
        self.year = year
        self.imdb = imdb
        self.cover = cover
        self.subtitles = subtitles

    def __str__(self):
        return self.title

    @classmethod
    def from_url(cls, url):
        soup = soup_for(url)
        content = soup.find("div", "subtitles")
        header = content.find("div", "box clearfix")

        cover = header.find("div", "poster").img.get("src")

        title = header.find("div", "header").h2.text[:-12].strip()

        imdb = header.find("div", "header").h2.find("a", "imdb").get("href")

        year = header.find("div", "header").ul.li.text
        year = int(re.findall(r"[0-9]+", year)[0])

        rows = content.find("table").tbody.find_all("tr")
        subtitles = Subtitle.from_rows(rows)
        l = [i for i in subtitles if i is not None]

        return cls(title, year, imdb, cover, l)


# functions
def section_exists(soup, section):
    tag_part = SectionsParts[section]

    try:
        headers = soup.find("div", "search-result").find_all("h2")
    except AttributeError:
        return False

    for header in headers:
        if tag_part in header.text:
            return True

    return False


def get_first_film(soup, section):
    tag_part = SectionsParts[section]
    tag = None

    headers = soup.find("div", "search-result").find_all("h2")
    for header in headers:
        if tag_part in header.text:
            tag = header
            break

    if not tag:
        return

    url = SITE_DOMAIN + tag.findNext("ul").find("li").div.a.get("href")
    return Film.from_url(url)

def exists(it):
    return (it is not None)

def search(term, language, limit_to=SearchTypes.Exact):
    soup = soup_for("%s/subtitles/title?q=%s&l=%s" % (SITE_DOMAIN, term, language))


    if "Subtitle search by" in str(soup):
        rows = soup.find("table").tbody.find_all("tr")
        subtitles = Subtitle.from_rows(rows)
        l = [i for i in subtitles if i is not None]
        return Film(term, subtitles=l)

    for junk, search_type in SearchTypes.__members__.items():
        if section_exists(soup, search_type):
            return get_first_film(soup, search_type)

        if limit_to == search_type:
            return

def convert_encoding(data, new_coding = 'UTF-8'):
  encoding = cchardet.detect(data)['encoding']

  if new_coding.upper() != encoding.upper():
    data = data.decode(encoding, data).encode(new_coding)

  return data