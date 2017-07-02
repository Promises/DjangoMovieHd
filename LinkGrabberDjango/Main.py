# -*- coding: utf-8 -*-
# Module: default
# Author: Roman V. M.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urlparse import parse_qsl
import base64
from Crypto import Random
from Crypto.Cipher import AES
import time
import hashlib
import requests
from bs4 import BeautifulSoup
import json
import re
from cursesmenu import *
from cursesmenu.items import *
import urllib

key = "darth89@1234bhgdrasew@7813451234"
bs = 32
time = str(int(round(time.time() * 1000)))[0:10]
baseurl = "http://appmoviehd.info/admin/index.php/apiandroid/"

# Free sample videos are provided by www.vidsplay.com
# Here we use a fixed set of properties simply for demonstrating purposes
# In a "real life" plugin you will need to get info and links to video files/streams
# from some web-site or online service.
VIDEOS = {'Movies': [{'param': 'movies?type=popular',
                      'title': 'Movies'}
                     ],
          'TV-shows': [{'param': 'tvshow?type=popular',
                        'title': 'TV-shows'}
                       ],
          'Search': [{'param': 'movies?type=search&keyword=',
                      'title': 'Search'}
                     ]}


def get_categories():
    """
    Get the list of video categories.
    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.
    :return: list
    """
    return VIDEOS.keys()




def get_videos(category):
    """
    Get the list of videofiles/streams.
    Here you can insert some parsing code that retrieves
    the list of videostreams in a given category from some site or server.
    :param category: str
    :return: list
    """
    return VIDEOS[category]





def list_videos(category, page):
    """
    Create the list of playable videos in the Kodi interface.
    :param category: str
    """
    # Get the list of videos in the category.
    videos = get_videos(category)
    # xbmc.log(GUIEditExportName(""))
    # Create a list for our items.
    # print videos[0]["param"]
    if category == "Search":
        xbmc.log("Search")

        keyword = GUIEditExportName("")
        videourl = baseurl + videos[0]['param'] + keyword + "&page=" + page + "&count=32&"
        # xbmc.log(videourl)
        r = requests.get(videourl + getToken()).text
        # xbmc.log(r)
        # xbmc.log(baseurl + getToken())
        testtext = decrypt(r)
        text = testtext[testtext.index("{"):][:-1]
        # xbmc.log(text)

        videos2 = json.loads(text)

        # for movie in videos2["films"]:
        # print movie["title"].encode('utf-8')
        # print(data["films"])
        listing = []
        # Iterate through videos.
        for video in videos2["films"]:
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=video['title'].encode('utf-8'))
            # Set additional info for the list item.
            list_item.setInfo('video', {'title': video['title'].encode('utf-8')})
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            # Here we use the same image for all items for simplicity's sake.
            # In a real-life plugin you need to set each image accordingly.
            list_item.setArt({'thumb': video['poster'], 'icon': video['poster']})
            # Set 'IsPlayable' property to 'true'.
            # This is mandatory for playable items!
            list_item.setProperty('IsPlayable', 'false')
            # Create a URL for the plugin recursive callback.
            # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
            if str(videos[0]["title"]) == "Movies":
                url = "http://www.vidsplay.com/vids/crab.mp4"
                url = '{0}?action=get&movie={1}'.format(_url, video['id']) + "&poster=".format(_url, video["poster"])
            else:
                videoid = video['id'] + "F"
                url = '{0}?action=get&movie={1}'.format(_url, videoid)
                print url
            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = True
            # Add our item to the listing as a 3-element tuple.
            listing.append((url, list_item, is_folder))
        if videos2["more"] == "yes":
            list_item = xbmcgui.ListItem(label=">>> Next Page >>>".encode('utf-8'))
            list_item.setProperty('IsPlayable', 'false')
            is_folder = True
            nextpage = int(page) + 1
            url = '{0}?action=listing&category={1}'.format(_url, videos[0]["title"]) + "&page={1}".format(_url,
                                                                                                          nextpage)
            listing.append((url, list_item, is_folder))
        # Add our listing to Kodi.
        # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
        # instead of adding one by ove via addDirectoryItem.
        xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(_handle)

    else:
        videourl = baseurl + videos[0]['param'] + "&genres=0&page=" + page + "&count=100&"
        r = requests.get(videourl + getToken()).text
        # xbmc.log(r)
        # xbmc.log(baseurl + getToken())
        testtext = decrypt(r)
        text = testtext[testtext.index("{"):][:-1]
        # xbmc.log(text)

        videos2 = json.loads(text)

        # for movie in videos2["films"]:
        # print movie["title"].encode('utf-8')
        # print(data["films"])
        listing = []
        # Iterate through videos.
        for video in videos2["films"]:
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=video['title'].encode('utf-8'))
            # Set additional info for the list item.
            list_item.setInfo('video', {'title': video['title'].encode('utf-8')})
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            # Here we use the same image for all items for simplicity's sake.
            # In a real-life plugin you need to set each image accordingly.
            list_item.setArt({'thumb': video['poster'], 'icon': video['poster']})
            # Set 'IsPlayable' property to 'true'.
            # This is mandatory for playable items!
            list_item.setProperty('IsPlayable', 'false')
            # Create a URL for the plugin recursive callback.
            # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
            if str(videos[0]["title"]) == "Movies":
                url = "http://www.vidsplay.com/vids/crab.mp4"
                url = '{0}?action=get&movie={1}'.format(_url, video['id']) + "&poster=".format(_url, video["poster"])
            else:
                videoid = video['id'] + "F"
                url = '{0}?action=get&movie={1}'.format(_url, videoid)
                print url
            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = True
            # Add our item to the listing as a 3-element tuple.
            listing.append((url, list_item, is_folder))
        if videos2["more"] == "yes":
            list_item = xbmcgui.ListItem(label=">>> Next Page >>>".encode('utf-8'))
            list_item.setProperty('IsPlayable', 'false')
            is_folder = True
            nextpage = int(page) + 1
            url = '{0}?action=listing&category={1}'.format(_url, videos[0]["title"]) + "&page={1}".format(_url,
                                                                                                          nextpage)
            listing.append((url, list_item, is_folder))
        # Add our listing to Kodi.
        # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
        # instead of adding one by ove via addDirectoryItem.
        xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.
    :param path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


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
    soup = BeautifulSoup(c, "html5lib")
    versiontxt= (soup.find_all("span", class_="version")[0].string)
    version = "".join(_ for _ in versiontxt if _ in ".1234567890")
    token = "ddteam@android@nanana" + time
    token = hashlib.md5(token.encode('utf-8')).hexdigest().upper()

    params = "os=android" + "&version=" + version + "&token=" + token + "&time=" + time + "&ads=0&deviceid=867271029048005"

    return params


def list_episodes(id):
    id = id[:-1]

    idget = "http://appmoviehd.info/admin/index.php/apiandroid/detail?id=" + id + "&page=1&count=-1&"
    r = requests.get(idget + getToken()).text
    # xbmc.log(r)
    # xbmc.log(baseurl + getToken())
    testtext = decrypt(r)
    text = testtext[testtext.index("{"):][:-1]
    xbmc.log(text)

    videos2 = json.loads(text)
    # for movie in videos2["films"]:
    # print movie["title"].encode('utf-8')
    # print(data["films"])
    listing = []
    # Iterate through videos.
    for video in videos2["chapters"]:

        # xbmc.log(text)

        # print text3


        # print videos3
        if text <= 10:
            print "nolinks"

        else:

            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=video['title'].encode('utf-8'))
            # Set additional info for the list item.
            list_item.setInfo('video', {'title': video['title'].encode('utf-8')})
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            # Here we use the same image for all items for simplicity's sake.
            # In a real-life plugin you need to set each image accordingly.
            # Set 'IsPlayable' property to 'true'.
            # This is mandatory for playable items!
            list_item.setProperty('IsPlayable', 'false')
            # Create a URL for the plugin recursive callback.
            # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
            # link = videos["id"]
            # url = urllib.unquote(link).decode('utf8')
            url = '{0}?action=getepisode&episode={1}'.format(_url, video['id'] + "&")
            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = True
            # Add our item to the listing as a 3-element tuple.
            listing.append((url, list_item, is_folder))

    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_links(id):
    idget = "http://appmoviehd.info/admin/index.php/apiandroid/detail?id=" + id + "&page=1&count=-1&"
    r = requests.get(idget + getToken()).text
    # xbmc.log(r)
    # xbmc.log(baseurl + getToken())
    testtext = decrypt(r)
    text = testtext[testtext.index("{"):][:-1]
    xbmc.log(text)

    videos2 = json.loads(text)
    # for movie in videos2["films"]:
    # print movie["title"].encode('utf-8')
    # print(data["films"])
    listing = []
    # Iterate through videos.
    for video in videos2["chapters"]:
        streamurl = "http://appmoviehd.info/admin/index.php/apiandroid/stream?chapterid=" + video[
            "id"] + "&page=1&count=-1&"
        r = requests.get(streamurl + getToken()).text
        test3 = decrypt(r)
        text3 = test3[test3.index("{"):][:-1]
        # xbmc.log(text)

        # print text3


        # print videos3
        if text <= 10:
            print "nolinks"

        else:
            videos3 = json.loads('{"bar":[' + text3 + "}")
            for videos in videos3["bar"]:
                # Create a list item with a text label and a thumbnail image.
                list_item = xbmcgui.ListItem(label=videos['name'].encode('utf-8'))
                # Set additional info for the list item.
                list_item.setInfo('video', {'title': videos['name'].encode('utf-8')})
                # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
                # Here we use the same image for all items for simplicity's sake.
                # In a real-life plugin you need to set each image accordingly.
                # Set 'IsPlayable' property to 'true'.
                # This is mandatory for playable items!
                list_item.setProperty('IsPlayable', 'true')
                # Create a URL f
                # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
                # instead of adding one by oor the plugin recursive callback.
                # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
                link = videos["link"]
                url = urllib.unquote(link).decode('utf8')
                # Add the list item to a virtual Kodi folder.
                # is_folder = False means that this item won't open any sub-list.
                is_folder = False
                # Add our item to the listing as a 3-element tuple.
                listing.append((url, list_item, is_folder))

    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def getstreamsEP(id):
    streamurl = "http://appmoviehd.info/admin/index.php/apiandroid/stream?chapterid=" + id + "&page=1&count=-1&"
    r = requests.get(streamurl + getToken()).text
    test3 = decrypt(r)
    text3 = test3[test3.index("{"):][:-1]
    # xbmc.log(text)
    listing = []

    # print text3



    videos3 = json.loads('{"bar":[' + text3 + "}")
    for videos in videos3["bar"]:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=videos['name'].encode('utf-8'))
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': videos['name'].encode('utf-8')})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL f
        # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
        # instead of adding one by oor the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
        link = videos["link"]
        url = urllib.unquote(link).decode('utf8')
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))

    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def subMenumake(id):
    print(id)
    submenu = CursesMenu("tet", "test")
    idget = "http://appmoviehd.info/admin/index.php/apiandroid/detail?id=" + id + "&page=1&count=-1&"
    r = requests.get(idget + getToken()).text
    # xbmc.log(r)
    # xbmc.log(baseurl + getToken())
    testtext = decrypt(r)
    text = testtext[testtext.index("{"):][:-1]

    videos2 = json.loads(text)
    # for movie in videos2["films"]:
    # print movie["title"].encode('utf-8')
    # print(data["films"])
    listing = []
    # Iterate through videos.
    for video in videos2["chapters"]:

        # xbmc.log(text)

        # print text3


        # print videos3
        if text <= 10:
            print "nolinks"

        else:

            """ # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=video['title'].encode('utf-8'))
            # Set additional info for the list item.
            list_item.setInfo('video', {'title': video['title'].encode('utf-8')})
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            # Here we use the same image for all items for simplicity's sake.
            # In a real-life plugin you need to set each image accordingly.
            # Set 'IsPlayable' property to 'true'.
            # This is mandatory for playable items!
            list_item.setProperty('IsPlayable', 'false')
            # Create a URL for the plugin recursive callback.
            # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
            # link = videos["id"]
            # url = urllib.unquote(link).decode('utf8')
            url = '{0}?action=getepisode&episode={1}'.format(_url, video['id'] + "&")
            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = True
            # Add our item to the listing as a 3-element tuple.
            listing.append((url, list_item, is_folder))"""
            submenu_item = SubmenuItem(video['title'].encode('utf-8'), subMenumake(video['id'].encode('utf-8')), menu)
            submenu.append_item(submenu_item)


    #function_item = FunctionItem("Call a Python function", input, ["Enter an input"])
    #submenu.append_item(function_item)
    return submenu

def createmainlisting():
    # Once we're done creating them, we just add the items to the menu
    videourl = baseurl + "movies?type=search&keyword=" + "how i met" + "&page=" + "1" + "&count=32&"
    r = requests.get(videourl + getToken()).text

    testtext = decrypt(r)
    text = testtext[testtext.index("{"):][:-1]

    videos2 = json.loads(text)
    for video in videos2["films"]:
        print("Title = " + video['title'].encode('utf-8') + ", id = " + video['id'].encode('utf-8'))
        # function_item = FunctionItem(video['title'].encode('utf-8'), input, ["Enter an input"])
        submenu_item = SubmenuItem(video['title'].encode('utf-8'), subMenumake(video['id'].encode('utf-8')), menu)

        menu.append_item(submenu_item)


menu = CursesMenu("Title", "Subtitle")

# Create some items

# MenuItem is the base class for all items, it doesn't do anything when selected
menu_item = MenuItem("Menu Item")

# A FunctionItem runs a Python function when selected
function_item = FunctionItem("Call a Python function", input, ["Enter an input"])

# A CommandItem runs a console command
command_item = CommandItem("Run a console command",  "touch hello.txt")

# A SelectionMenu constructs a menu from a list of strings
selection_menu = SelectionMenu({"item1":1, "item2":2, "item3":3})

# A SubmenuItem lets you add a menu (the selection_menu above, for example)
# as a submenu of another menu
submenu_item = SubmenuItem("Submenu item", selection_menu, menu)

createmainlisting()

menu.append_item(menu_item)

menu.append_item(command_item)
menu.append_item(submenu_item)

# Finally, we call show to show the menu and allow the user to interact
menu.show()






"""
videourl = baseurl + "movies?type=search&keyword=" + "How I met your mother" + "&page=" + "1" + "&count=32&"
# xbmc.log(videourl)
r = requests.get(videourl + getToken()).text
# xbmc.log(r)
# xbmc.log(baseurl + getToken())
testtext = decrypt(r)
text = testtext[testtext.index("{"):][:-1]

videos2 = json.loads(text)

# for movie in videos2["films"]:
# print movie["title"].encode('utf-8')
# print(data["films"])
listing = []
# Iterate through videos.
for video in videos2["films"]:
    print("Title = " + video['title'].encode('utf-8') + ", id = " + video['id'].encode('utf-8'))
"""

"""
    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label=video['title'].encode('utf-8'))
    # Set additional info for the list item.
    list_item.setInfo('video', {'title': video['title'].encode('utf-8')})
    # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
    # Here we use the same image for all items for simplicity's sake.
    # In a real-life plugin you need to set each image accordingly.
    list_item.setArt({'thumb': video['poster'], 'icon': video['poster']})
    # Set 'IsPlayable' property to 'true'.
    # This is mandatory for playable items!
    list_item.setProperty('IsPlayable', 'false')
    # Create a URL for the plugin recursive callback.
    # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4

    videoid = video['id'] + "F"
    url = '{0}?action=get&movie={1}'.format(_url, videoid)
    print url
    # Add the list item to a virtual Kodi folder.
    # is_folder = False means that this item won't open any sub-list.
    is_folder = True
    # Add our item to the listing as a 3-element tuple.
    listing.append((url, list_item, is_folder))
if videos2["more"] == "yes":
    list_item = xbmcgui.ListItem(label=">>> Next Page >>>".encode('utf-8'))
    list_item.setProperty('IsPlayable', 'false')
    is_folder = True
    nextpage = int(page) + 1
    url = '{0}?action=listing&category={1}'.format(_url, videos[0]["title"]) + "&page={1}".format(_url,
                                                                                                  nextpage)
    listing.append((url, list_item, is_folder))
# Add our listing to Kodi.
# Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
# instead of adding one by ove via addDirectoryItem.
xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    """