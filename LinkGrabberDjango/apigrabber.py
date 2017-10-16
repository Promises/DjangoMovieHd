import base64
import hashlib
import json
import time
import requests
from django.utils import timezone
from LinkGrabberDjango.models import Setting
from pyimei import ImeiSupport
from Crypto import Random
from Crypto.Cipher import AES
import sys
reload(sys)
from .lib import requests_cache

sys.setdefaultencoding("utf8")

key = "darth19@1234bhgdrasew@1094561234"
bs = 32
currenttimems = str(int(round(time.time() * 1000)))[0:10]
baseurl = "http://appmoviehd.info/admin/index.php/apiandroid2/"

requests_cache.install_cache('movieshd_cache', backend='sqlite', expire_after=30,ignored_parameters=['time',"os", "version","token", "tokengoogle","ads","deviceid"])

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
    #result = requests.get("http://appmoviehd.info/")
    #c = result.content
    #soup = BeautifulSoup(c,"lxml")
    #versiontxt = (soup.find_all("span", class_="version")[0].string)
    #version = "".join(_ for _ in versiontxt if _ in ".1234567890")
    version = Setting.objects.get(Status="Current").AppVersion
    token = "ttteam@android@122334" + currenttimems
    token = hashlib.md5(token.encode('utf-8')).hexdigest().upper()
    params = {'os': 'android', 'version': version, 'token': token, 'tokengoogle': '', 'time': currenttimems, 'ads': '0','deviceid': ImeiSupport.generateNew() }
    return params

def apirequest(suffix, apiparams):
    params = getToken().copy()
    params.update(apiparams)
    response = requests.get(baseurl + suffix,params=params)
    r = response.text
    testtext = decrypt(r)
    text = testtext[testtext.index("{"):][:-1]
    jsonResponse = json.loads(text)
    return jsonResponse

def getpopular(type):
    params = {'type': 'updated', 'page': '1', 'count':'10'}
    suffix = type
    videos2 = apirequest(suffix,params)

    return videos2["films"]

def createmainlisting(name):
    params = {'type': 'search', 'keyword': name, 'page':'1','count':'10'}
    suffix = "movies"
    videos2 = apirequest(suffix,params)

    return videos2["films"]


def createdetails(id):

    params = {'id': id, 'page':'1','count':'-1'}
    suffix = "detail"
    videos2 = apirequest(suffix,params)

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
    with requests_cache.disabled():
        streamurl = baseurl + "stream?chapterid=" + id + "&page=1&count=-1&"
        r = requests.get(streamurl, params=getToken()).text
        test3 = decrypt(r)
        text3 = test3[test3.index("{"):][:-1]
        videos3 = json.loads('{"bar":[' + text3 + "}")
        print test3
        return videos3["bar"]




def getToplist(type, page, sort):
    allvids = []
    notlast = "yes"
    currentpage = 1

    while notlast == "yes":
        params = {'type': sort, 'page': str(currentpage), 'count': '5000'}
        suffix = type
        videos2 = apirequest(suffix, params)
        allvids += videos2["films"]
        notlast = videos2["more"]
        currentpage += 1

    return allvids

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

def testtime():
    start_time = time.time()
    print getToplist("movies",1,"popular")
    print("---- %s seconds ----" % (time.time() - start_time))
