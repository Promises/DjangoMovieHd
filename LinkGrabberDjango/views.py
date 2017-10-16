from __future__ import print_function

import urllib

from bs4 import BeautifulSoup
import HTMLParser
import json
import re
import unicodedata
import zipfile
from StringIO import StringIO
from collections import Counter

import magic
import requests
from digg_paginator import DiggPaginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.views.generic import View
from notifications.signals import notify
from pycaption import CaptionConverter, SRTReader, WebVTTWriter
from rest_framework import authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from LinkGrabberDjango import apigrabber
from LinkGrabberDjango.forms import User, FeatureRequestForm
from LinkGrabberDjango.templatetags.links_extras import sslimage
from .api import subscene
from .forms import UserForm, UserLoginForm
from .models import watched, Profile, favourite, FeatureRequest


def post_list(request):
    pagename = "Search Results"
    a = request.GET.get('id', 'The Walking Dead').replace("'", r"\'")
    results = apigrabber.createmainlisting(a)
    return render(request, 'gui/menumain.html', {"posts": results, "pagename": pagename})


def post_detail(request, id, title):
    seen = False
    isFavourite = False
    seenlist = []

    if request.user.is_authenticated():
        try:
            favourite.objects.get(user=request.user.username,
                                  showid=id, )
            isFavourite = True


            # if we get this far, we have an exact match for this form's data
        except favourite.DoesNotExist:
            # because we didn't get a match
            isFavourite = False

            pass
        seen = watched.objects.filter(user=request.user.username,
                                      showid=id, )
        for key in seen:
            seenlist.append(key.epid)
    jsonseen = json.dumps(seenlist)

    return render(request, 'gui/post_detail.html', {
                                                    "isplay": True,
                                                    "showid": id,
                                                    "seen": seen,
                                                    "jsonseen": jsonseen,
                                                    "isfav": isFavourite,
                                                    "pagename": title
                                                    })


def play(request, epid, streamid, showid):
    data = apigrabber.getstreams(epid)
    showinfo = apigrabber.createdetails(showid)
    otherepisodes = showinfo["posts"]
    index = otherepisodes.index((item for item in otherepisodes if item["id"] == epid).next())

    nextep = False
    prevep = False
    isshow = False
    show = showinfo["title"].encode('utf-8').strip()
    poster = showinfo["poster"]

    if len(otherepisodes) > 3:
        eptitle = otherepisodes[1]['title'].encode('utf-8').strip().replace(u'\xa0', u' ')
        if len(otherepisodes) == index + 1:
            print("first episode")
        else:
            prevep = otherepisodes[index + 1]
        if apigrabber.find_between(eptitle, "S", "E"):
            isshow = True
        if otherepisodes[index - 1]:
            nextep = otherepisodes[index - 1]

    showid = showid
    if isshow:
        pagename = otherepisodes[index]['title'].encode('utf-8').strip()
    else:
        pagename = show

    isplay = True
    post = data[int(streamid)]
    isyt = False
    if post["link"].startswith("GoogleDrive"):
        isyt = True

    return render(request, 'gui/play.html', {'title': id,
                                             "isplay": isplay,
                                             "id": epid,
                                             "poster": poster,
                                             "pagename": pagename,
                                             "isyt": isyt,
                                             "post": post,
                                             "next": nextep, "prev": prevep, "show": show, "showid": showid,
                                             "isshow": isshow})


def subtitle(request, title, no):
    t = re.sub('\(.*?\)', '', title)[:-1]
    film = subscene.search(t, "English")

    zip = requests.get(subscene.zipped_url(film.subtitles[int(no)]))

    fp = StringIO(zip.content)
    archive = zipfile.ZipFile(fp, 'r')
    srt = archive.read(archive.namelist()[0])
    soup = BeautifulSoup(srt)
    # print(soup.originalEncoding)
    converter = CaptionConverter()
    unistring = unicode(srt.decode(soup.originalEncoding))
    if "utf-8" in soup.originalEncoding:
        unistring = unistring[1:]
    converter.read(unistring, SRTReader())
    html_parser = HTMLParser.HTMLParser()

    return HttpResponse(html_parser.unescape(converter.write(WebVTTWriter()).encode('ascii', 'ignore')),
                        content_type="text/vtt")


def home(request):
    favourites = favourite.objects.filter(user=request.user.username, ).order_by("date").reverse()[:10]
    return render(request, 'gui/home.html',
                  {"pagename": "Home", "favourites": favourites})


class browseTopList(View):
    def get(self, request):
        type = request.GET.get('cat')
        page = request.GET.get('page', 1)
        sort = request.GET.get('sort', "popular")
        toplist = apigrabber.getToplist(type, page, sort)
        # print(len(toplist))
        paginator = DiggPaginator(toplist, 24, body=6)
        try:
            movies = DiggPaginator.page(paginator, number=page)
        except PageNotAnInteger:
            movies = DiggPaginator.page(paginator, number=1)
        except EmptyPage:
            movies = DiggPaginator.page(paginator, number=DiggPaginator.num_pages)

        return render(request, 'gui/toplist.html',
                      {"posts": movies, "type": type, "page": int(page), "pagename": "Browse Top List"})


class browseFavourites(View):
    def get(self, request):
        page = request.GET.get('page', 1)
        favourites_list = favourite.objects.filter(user=request.user.username, ).order_by("date").reverse()
        paginator = Paginator(favourites_list, 10)
        try:
            favourites = paginator.page(page)
        except PageNotAnInteger:
            favourites = paginator.page(1)
        except EmptyPage:
            favourites = paginator.page(paginator.num_pages)
        return render(request, 'gui/favourites.html',
                      {"posts": favourites, "page": int(page), "pagename": "Browse Top List"})


class links(View):
    def post(self, request):
        show = unicodedata.normalize("NFKD", request.POST.get("foo").replace(u'\xa0', u' '))
        epid = request.POST.get("epid")
        epname = unicodedata.normalize("NFKD", request.POST.get("epname").replace(u'\xa0', u' '))
        showid = request.POST.get("showid")
        links = apigrabber.getstreams(epid)

        if request.user.is_authenticated():
            user = User.objects.get(pk=request.user.id)
            w = watched(user=request.user.username, epid=epid, epname=epname.encode('utf-8').strip(), showid=showid,
                        showname=show.encode('utf-8').strip())

            try:
                watched.objects.get(user=request.user.username,
                                    epid=epid,
                                    epname=epname.encode('utf-8').strip(),
                                    showid=showid,
                                    showname=show.encode('utf-8').strip())

                # if we get this far, we have an exact match for this form's data
            except watched.DoesNotExist:
                # because we didn't get a match
                w.save()
                pass
            if user.profile.autoplaybest:
                bestq = None
                for link in links:
                    if not bestq:
                        quality = apigrabber.find_between(link["name"], "Video ", " (")

                        if quality.encode('utf-8') == "1080p":
                            bestq = link["type"]
                        elif quality.encode('utf-8') == "720p":
                            bestq = link["type"]
                        elif quality.encode('utf-8') == "480p":
                            bestq = link["type"]
                        elif quality.encode('utf-8') == "360p":
                            bestq = link["type"]
                        elif link["name"].startswith("Google Direct"):
                            bestq = link["type"]

                return redirect('plays', showid=showid, epid=epid, streamid=bestq)
        return render(request, 'gui/links.html', {'posts': links, "pagename": epname, "showid": showid})


class SearchSubmitView(View):
    template = 'gui/search_submit.html'
    response_message = 'This is the response'

    def post(self, request):
        template = loader.get_template(self.template)
        query = request.POST.get('search', '')

        # A simple query for Item objects whose title contain 'query'
        items = apigrabber.createmainlisting(query)

        context = {'title': self.response_message, 'query': query, 'items': items}

        rendered_template = template.render(context, request)
        return HttpResponse(rendered_template, content_type='text/html')


class SearchAjaxSubmitView(SearchSubmitView):
    template = 'gui/search_results.html'
    response_message = 'This is the AJAX response'


class UserFormView(View):
    title = "Register"
    form_class = UserForm
    template_name = "gui/user/form.html"

    # blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {"form": form, "title": self.title})

    # submit
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user.set_password(password)
            user.save()


            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("home")
        return render(request, self.template_name, {"form": form, "title": self.title, "pagename": self.title})


class UserLoginView(View):
    title = "Login"

    # blank form
    def get(self, request):
        form = UserLoginForm(None)
        return render(request, "gui/user/form.html", {"form": form, "title": self.title, "pagename": self.title})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            login(request, user)
            # redirect()
            return redirect("home")

        return render(request, "gui/user/form.html", {"form": form, "title": self.title, "pagename": self.title})


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        # redirect
        return redirect("home")


class UserProfileView(View):
    # blank form
    def post(self, request):
        form = FeatureRequestForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.date = timezone.now()
            post.save()

        return redirect('profile')

    def get(self, request, foo=False):
        if request.user.is_authenticated:
            title = request.user.username
            form_class = FeatureRequestForm
            obj = get_object_or_404(User, pk=request.user.id)
            # obj.notifications.unread().mark_all_as_read()
            requests = FeatureRequest.objects.filter(user=request.user)
            notifications = request.user.notifications.unread().order_by('-timestamp')
            if request.user.is_superuser:
                requests = FeatureRequest.objects.all()
            return render(request, "gui/user/profile.html",
                          {'form': form_class, "title": title, "pagename": title, "settings": obj, "submitted": foo,
                           "requests": requests, 'notifications': notifications})
        return HttpResponseRedirect(reverse('home'))


class AutoPlaySwitchRedirect(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            obj = get_object_or_404(Profile, pk=user.id)
            if not obj.autoplaybest:
                obj.autoplaybest = True
            else:
                obj.autoplaybest = False
            obj.save()

        return HttpResponseRedirect(reverse('profile'))


class AutoPlayApiToggle(APIView):
    """
    View to toggle autoplay for current user.

    * Requires User
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        updated = False
        user = request.user
        if user.is_authenticated():
            if not user.profile.autoplaybest:
                user.profile.autoplaybest = True
            else:
                user.profile.autoplaybest = False
            user.save()
            updated = True
        data = {
            "updated": updated,
            "autoplay": user.profile.autoplaybest,
        }
        return Response(data)


class AutoPlayNextApiToggle(APIView):
    """
    View to toggle autplaynext for current user.

    * Requires User
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        updated = False
        user = request.user
        if user.is_authenticated():
            if not user.profile.autoplaynext:
                user.profile.autoplaynext = True
            else:
                user.profile.autoplaynext = False
            user.save()
            updated = True
        data = {
            "updated": updated,
            "autoplaynext": user.profile.autoplaynext,
        }
        return Response(data)


class NightModeApiToggle(APIView):
    """
    View to toggle Nightmode for current user.

    * Requires User
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        updated = False
        user = request.user
        if user.is_authenticated():
            if not user.profile.night_mode:
                user.profile.night_mode = True
            else:
                user.profile.night_mode = False
            user.save()
            updated = True
        data = {
            "updated": updated,
            "nightmode": user.profile.night_mode,
        }
        return Response(data)


class FavouriteApiToggle(APIView):
    """
    View to toggle autoplay for current user.

    * Requires User
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        updated = False
        user = request.user
        isFavourite = False
        showid = request.GET.get('id')
        dict = apigrabber.createdetails(showid)
        isshow = False
        if len(dict["posts"]) >= 10:
            if apigrabber.find_between(dict["posts"][1]["title"], "S", "E"):
                isshow = True

        if user.is_authenticated():
            w = favourite(user=user.username,
                          showid=showid,
                          showname=dict['title'].encode('utf-8').strip(),
                          show=isshow,
                          count=len(dict["posts"]),
                          poster=dict['poster'],
                          )

            try:
                favourite.objects.get(user=user.username,
                                      showid=showid, ).delete()
                isFavourite = False


                # if we get this far, we have an exact match for this form's data
            except favourite.DoesNotExist:
                # because we didn't get a match
                w.save()
                isFavourite = True

                pass
            updated = True
        data = {
            "updated": updated,
            "Favourite": isFavourite,
        }
        return Response(data)


class FiveRecommended(APIView):
    """
    View to toggle autoplay for current user.

    * Requires User
    """

    def get(self, request, format=None):
        showid = request.GET.get('id')
        favlist = favourite.objects.filter(
            user__in=favourite.objects.filter(showid=showid).values_list('user')).exclude(showid=showid).values_list(
            "showid")
        common = Counter(favlist).most_common(6)
        idlist = [word[0][0] for word in common]
        queryset = favourite.objects.filter(showid__in=idlist).distinct("showid")
        data = {
            "shows": [{'showid': item.showid, 'showname': item.showname, 'poster': sslimage(item.poster)} for item in
                      queryset]}
        return Response(data)


class getPopularAPI(APIView):
    """
    View to get popular for Front Page.
    """

    def get(self, request, format=None):
        type = request.GET.get('type')
        toplist = apigrabber.getpopular(type)
        data = {
            "shows": [{'showid': item["id"], 'showname': item["title"], 'poster': sslimage(item["poster"])} for item in
                      toplist]}
        return Response(data)


class getDetailsAPI(APIView):
    """
    View to get popular for Front Page.
    """

    def get(self, request, format=None):
        id = request.GET.get('id')
        dict = apigrabber.createdetails(id)
        data = {
            "show":
                {
                    "desc": dict["desc"],
                    "rating": dict['rating'],
                    "startyear": dict['startyear'],
                    "title": dict['title'].replace(u'\xa0', ' ').decode("utf-8","ignore").encode('utf-8').strip(),
                    "poster": sslimage(dict['poster']),
                    "state": dict['state'],
                    "genre": dict['genre'],
                    'posts': dict["posts"]
                }
        }
        return Response(data)


class GetNextEpisodeAPI(APIView):
    """
    View to toggle autoplay for current user.

    * Requires User
    """

    def get(self, request, format=None):
        showid = request.GET.get('showid')
        epid = request.GET.get('epid')
        # print(request.GET.get('epid'))
        showinfo = apigrabber.createdetails(showid)
        otherepisodes = showinfo["posts"]
        index = otherepisodes.index((item for item in otherepisodes if item["id"] == epid).next())
        nextep = otherepisodes[index - 1]
        links = apigrabber.getstreams(nextep["id"])
        bestq = None
        for link in links:
            if not bestq:
                quality = apigrabber.find_between(link["name"], "Video ", " (")
                source = "normal"

                if quality.encode('utf-8') == "1080p":
                    bestq = link["type"]
                elif quality.encode('utf-8') == "720p":
                    bestq = link["type"]
                elif quality.encode('utf-8') == "480p":
                    bestq = link["type"]
                elif quality.encode('utf-8') == "360p":
                    bestq = link["type"]
                elif link["name"].startswith("Google Direct"):
                    bestq = link["type"]
        data = apigrabber.getstreams(nextep["id"])

        url = urllib.unquote((item for item in data if item["type"] == int(bestq)).next()["link"]).decode('utf8')
        # print(index)

        if request.user.is_authenticated():
            user = User.objects.get(pk=request.user.id)
            showname = showinfo["title"]
            epname = otherepisodes[index]["title"]
            w = watched(user=request.user.username, epid=epid, epname=epname.encode('utf-8').strip(), showid=showid,
                        showname=showname.encode('utf-8').strip())

            try:
                watched.objects.get(user=request.user.username,
                                    epid=epid,
                                    showid=showid,
                                    )

                # if we get this far, we have an exact match for this form's data
            except watched.DoesNotExist:
                # because we didn't get a match
                w.save()
                pass
        data = {
            "shows": {'nextepid': nextep["id"], 'link': url, 'title': nextep["title"], "source": source, "type": bestq}}
        return Response(data)

class GetPrevEpisodeAPI(APIView):
    """
    View to toggle autoplay for current user.

    * Requires User
    """

    def get(self, request, format=None):
        showid = request.GET.get('showid')
        epid = request.GET.get('epid')
        # print(request.GET.get('epid'))
        showinfo = apigrabber.createdetails(showid)
        otherepisodes = showinfo["posts"]
        index = otherepisodes.index((item for item in otherepisodes if item["id"] == epid).next())
        prevep = otherepisodes[index + 1]
        links = apigrabber.getstreams(prevep["id"])
        bestq = None
        for link in links:
            if not bestq:
                quality = apigrabber.find_between(link["name"], "Video ", " (")
                source = "normal"

                if quality.encode('utf-8') == "1080p":
                    bestq = link["type"]
                elif quality.encode('utf-8') == "720p":
                    bestq = link["type"]
                elif quality.encode('utf-8') == "480p":
                    bestq = link["type"]
                elif quality.encode('utf-8') == "360p":
                    bestq = link["type"]
                elif link["name"].startswith("Google Direct"):
                    bestq = link["type"]
        data = apigrabber.getstreams(prevep["id"])

        url = urllib.unquote((item for item in data if item["type"] == int(bestq)).next()["link"]).decode('utf8')
        # print(index)

        if request.user.is_authenticated():
            user = User.objects.get(pk=request.user.id)
            showname = showinfo["title"]
            epname = otherepisodes[index]["title"]
            w = watched(user=request.user.username, epid=epid, epname=epname.encode('utf-8').strip(), showid=showid,
                        showname=showname.encode('utf-8').strip())

            try:
                watched.objects.get(user=request.user.username,
                                    epid=epid,
                                    epname=epname.encode('utf-8').strip(),
                                    showid=showid,
                                    showname=showname.encode('utf-8').strip())

                # if we get this far, we have an exact match for this form's data
            except watched.DoesNotExist:
                # because we didn't get a match
                w.save()
                pass
        data = {
            "shows": {'prevepid': prevep["id"], 'link': url, 'title': prevep["title"], "source": source,
                      "type": bestq}}
        return Response(data)


# tests:
def imageview(request, title):
    zip = requests.get(title)

    fakeimage = StringIO(zip.content)
    # image_data = open(fakeimage, "rb").read()
    return HttpResponse(fakeimage, content_type="image/png")


@login_required
def send_notification(request):
    recipient_username = request.POST.get('recipient_username', None)

    if recipient_username:
        recipients = User.objects.filter(username=recipient_username)
    else:
        recipients = User.objects.all()

    for recipient in recipients:
        notify.send(
            request.user,
            recipient=recipient,
            verb=request.POST.get('verb', '')
        )

    return HttpResponseRedirect(reverse('home'))


@login_required
def mark_as_read(request):
    request.user.notifications.unread().mark_all_as_read()

    return HttpResponseRedirect(reverse('home'))
