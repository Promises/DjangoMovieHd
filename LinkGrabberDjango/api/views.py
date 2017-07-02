from rest_framework import generics

from LinkGrabberDjango import apigrabber
from serializers import VideoSerializer
from object import VideoObject

class ViewTest(generics.CreateAPIView):

    serializer_class = VideoSerializer
    permission_classes = []
    authentication_classes = []


