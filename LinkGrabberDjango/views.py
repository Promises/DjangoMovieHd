from __future__ import print_function

import unicodedata

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.template import loader
from LinkGrabberDjango import apigrabber
from LinkGrabberDjango.forms import User
from .forms import UserForm, UserLoginForm
from .models import watched, Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
import json


def post_list(request):
    # return render(request, 'gui/menumain.html', {})
    pagename = "Search Results"
    a = request.GET.get('id', 'The Walking Dead')
    return render(request, 'gui/menumain.html', {"posts": apigrabber.createmainlisting(a), "pagename": pagename})


def post_detail(request, id):
    dict = apigrabber.createdetails(id)
    seen = False
    jsoneps =False
    print(len(dict["posts"]))
    if len(dict["posts"]) >= 10:
        if apigrabber.find_between(dict["posts"][1]["title"], "S", "E"):
            isshow = True
            print ("ishow")
            jsoneps = json.dumps(dict["posts"])

    if request.user.is_authenticated():
        seen = watched.objects.filter(user=request.user.username,
                                      showid=id, )

    return render(request, 'gui/post_detail.html', {'posts': dict["posts"],
                                                    'jsoneps': jsoneps,
                                                    "desc": dict["desc"],
                                                    "rating": dict['rating'],
                                                    "startyear": dict['startyear'],
                                                    "title": dict['title'].encode('utf-8').strip(),
                                                    "poster": dict['poster'],
                                                    "state": dict['state'],
                                                    "genre": dict['genre'],
                                                    "showid": id,
                                                    "seen": seen,
                                                    "pagename": dict["title"].encode("utf-8").strip()
                                                    })



def play(request, epid, streamid, showid):
    data = apigrabber.getstreams(epid)
    showinfo = apigrabber.createdetails(showid)
    otherepisodes = showinfo["posts"]
    index = otherepisodes.index((item for item in otherepisodes if item["id"] == epid).next())

    nextep = False
    prevep = False
    isshow = False
    show = showinfo["title"]

    if len(otherepisodes) > 3:
        eptitle = otherepisodes[1]['title'].encode('utf-8').strip().replace(u'\xa0', u' ')
        # if len(otherepisodes) == index:
        print(str(len(otherepisodes)) + ", " + str(index))
        if len(otherepisodes) == index + 1:
            print("first episodes")
        else:
            prevep = otherepisodes[index + 1]
        if apigrabber.find_between(eptitle, "S", "E"):
            isshow = True
        if otherepisodes[index - 1]:
            nextep = otherepisodes[index - 1]

    showid = showid
    return render(request, 'gui/play.html', {'title': id,
                                             "pagename": otherepisodes[index]['title'].encode('utf-8').strip().replace(
                                                 u'\xa0', u' '),
                                             "post": (item for item in data if item["id"] == streamid).next(),
                                             "next": nextep, "prev": prevep, "show": show, "showid": showid,
                                             "isshow": isshow})


def home(request):
    poptv = apigrabber.getpopular("tvshow")
    popmovies = apigrabber.getpopular("movies")
    return render(request, 'gui/home.html', {"poptv": poptv, "popmovies": popmovies, "pagename": "Home"})


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
            print(user.profile.autoplaybest)
            if user.profile.autoplaybest:
                bestq = None
                print(links)
                for link in links:
                    if not bestq:
                        quality = apigrabber.find_between(link["name"], "Video ", " (")
                        if quality.encode('utf-8') == "1080p":
                            bestq = link["id"]
                        elif quality.encode('utf-8') == "720p":
                            bestq = link["id"]
                        elif quality.encode('utf-8') == "480p":
                            bestq = link["id"]
                        elif quality.encode('utf-8') == "360p":
                            bestq = link["id"]
                print(bestq)
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
    def get(self, request):
        if request.user.is_authenticated:
            title = request.user.username
            obj = get_object_or_404(User, pk=request.user.id)
            return render(request, "gui/user/profile.html", {"title": title, "pagename": title, "settings": obj})
        return HttpResponseRedirect(reverse('home'))


class AutoPlaySwitchRedirect(View):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            obj = get_object_or_404(Profile, pk=user.id)
            print(user.username)
            if not obj.autoplaybest:
                obj.autoplaybest = True
            else:
                obj.autoplaybest = False
            obj.save()
            print(obj.autoplaybest)

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
        liked = False
        user = request.user
        if user.is_authenticated():
            obj = get_object_or_404(Profile, pk=user.id)
            print(user.username)
            if not obj.autoplaybest:
                obj.autoplaybest = True
            else:
                obj.autoplaybest = False
            obj.save()
            updated = True
        data = {
            "updated": updated,
            "autoplay": obj.autoplaybest,
        }
        print(obj.autoplaybest)
        return Response(data)
