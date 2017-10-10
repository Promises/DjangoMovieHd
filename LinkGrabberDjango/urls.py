from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^searchaskforapi/', views.post_list, name='post_list'),
    url(r'^search_submit/', views.SearchSubmitView.as_view(), name='search-submit'),
    url(r'^search_ajax_submit/', views.SearchAjaxSubmitView.as_view(), name='search-ajax-submit'),

    url(r'^$', views.home, name='home'),

    url(r'^post/(?P<id>\d+)/(?P<title>.*)/$', views.post_detail, name='post_detail'),
    url(r'^link/', views.links.as_view(), name='links'),
    url(r'^play/(?P<showid>.*)/(?P<epid>.*)/(?P<streamid>.*)$', views.play, name='plays'),
    url(r'^subtitle.vtt/(?P<title>.*)/(?P<no>\d+)/$', views.subtitle, name='subtitle'),
    url(r'^browse/$', views.browseTopList.as_view(), name='toplist'),
    url(r'^favourites/$', views.browseFavourites.as_view(), name='favourites'),

    url(r'^register/$', views.UserFormView.as_view(), name='register'),
    url(r'^login/$', views.UserLoginView.as_view(), name='login'),
    url(r'^logout/$', views.UserLogoutView.as_view(), name='logout'),
    url(r'^account/$', views.UserProfileView.as_view(), name='profile'),
    url(r'^account/autoplay$', views.AutoPlaySwitchRedirect.as_view(), name='AutoPlaySwitch'),
    url(r'^api/account/favourite$', views.FavouriteApiToggle.as_view(), name='favourite'),

    url(r'^api/account/autoplay$', views.AutoPlayApiToggle.as_view(), name='AutoPlayApiToggle'),
    url(r'^api/account/nightmode', views.NightModeApiToggle.as_view(), name='NightModeApiToggle'),
    url(r'^api/account/autoplaynext', views.AutoPlayNextApiToggle.as_view(), name='AutoPlayNextApiToggle'),
    url(r'^api/account/fiverecommended', views.FiveRecommended.as_view(), name='FiveRecommendedApiView'),
    url(r'^api/media/GetNextEpisode', views.GetNextEpisodeAPI.as_view(), name='GetNextEpisodeApi'),
    url(r'^api/media/GetPrevEpisode', views.GetPrevEpisodeAPI.as_view(), name='GetPrevEpisodeApi'),

    url(r'^api/media/getPopular', views.getPopularAPI.as_view(), name='getPopularAPI'),
    url(r'^api/media/getDetails', views.getDetailsAPI.as_view(), name='getDetails'),

    url(r'^send_notification/$', views.send_notification, name='send_notification'),
    url(r'^mark_as_read/$', views.mark_as_read, name='mark_as_read'),

    url(r'^imagereturn/(?P<title>.*)$', views.imageview, name='sslimage'),

]
