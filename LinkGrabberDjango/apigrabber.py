import base64
import hashlib
import json
import time

import requests
from Crypto import Random
from Crypto.Cipher import AES
from bs4 import BeautifulSoup

key = "darth89@1234bhgdrasew@7813451234"
bs = 32
time = str(int(round(time.time() * 1000)))[0:10]
baseurl = "http://appmoviehd.info/admin/index.php/apiandroid/"


def encrypt(raw):
    raw = _pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw))


def decrypt(enc):
    enc = base64.b64decode(enc)
    iv = enc[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return _unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')


def _pad(s):
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)


def _unpad(s):
    return s[:-ord(s[len(s) - 1:])]


def getToken():
    result = requests.get("http://appmoviehd.info/")
    c = result.content
    soup = BeautifulSoup(c,"lxml")
    versiontxt = (soup.find_all("span", class_="version")[0].string)
    version = "".join(_ for _ in versiontxt if _ in ".1234567890")
    token = "ddteam@android@nanana" + time
    token = hashlib.md5(token.encode('utf-8')).hexdigest().upper()

    params = "os=android" + "&version=" + version + "&token=" + token + "&time=" + time + "&ads=0&deviceid=867271029048005"

    return params


def createmainlisting(name):
    # Once we're done creating them, we just add the items to the menu
    #print name

    videourl = baseurl + "movies?type=search&keyword=" + name + "&page=" + "1" + "&count=5000&"
    r = requests.get(videourl + getToken()).text

    testtext = decrypt(r)
    text = testtext[testtext.index("{"):][:-1]

    videos2 = json.loads(text)

    return videos2["films"]


def getpopular(type):
    videourl = baseurl + type + "?type=updated&page=" + "1" + "&count=10&"
    r = requests.get(videourl + getToken()).text

    testtext = decrypt(r)
    #print testtext
    text = testtext[testtext.index("{"):][:-1]

    videos2 = json.loads(text)

    return videos2["films"]


def createdetails(id):
    idget = "http://appmoviehd.info/admin/index.php/apiandroid/detail?id=" + id + "&page=1&count=-1&"
    r = requests.get(idget + getToken()).text
    # xbmc.log(r)
    # xbmc.log(baseurl + getToken())
    testtext = decrypt(r)
    text = testtext[testtext.index("{"):][:-1]

    videos2 = json.loads(text)

    return {"posts": videos2["chapters"],
            "desc": videos2["desc"],
            "rating": videos2['rating'],
            "startyear": videos2['startyear'],
            "title": videos2['title'],
            "poster": videos2['poster'],
            "state": videos2['state'],
            "genre": videos2['genre'],
            }


def getstreams(id):
    streamurl = "http://appmoviehd.info/admin/index.php/apiandroid/stream?chapterid=" + id + "&page=1&count=-1&"
    r = requests.get(streamurl + getToken()).text
    test3 = decrypt(r)
    text3 = test3[test3.index("{"):][:-1]
    videos3 = json.loads('{"bar":[' + text3 + "}")
    print test3
    return videos3["bar"]


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def getToplist(type, page, sort):
    allvids = []
    notlast = "yes"
    currentpage = 1

    while notlast == "yes":
        videourl = baseurl + type + "?type=" + sort + "&page=" + str(currentpage) + "&count=5000&"
        r = requests.get(videourl + getToken()).text
        testtext = decrypt(r)
        text = testtext[testtext.index("{"):][:-1]
        videos2 = json.loads(text)
        allvids += videos2["films"]
        notlast = videos2["more"]
        #print videos2["more"]
        #print currentpage
        currentpage += 1

    return allvids