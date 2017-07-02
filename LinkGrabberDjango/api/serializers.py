from rest_framework import serializers

from LinkGrabberDjango.api.object import VideoObject


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoObject
        fields = ["id"]
        #fields = ["posts", "desc", "rating", "startyear", "title", "poster", "state", "genre" ]

    def get_values(self, value):
        id =value
        qs = apigrabber.createdetails(id)
        return {
    1: VideoObject(
        posts = reversed(tasks2["posts"]),
        desc= tasks2["desc"],
        rating= tasks2['rating'],
        startyear= tasks2['startyear'],
        title= tasks2['title'],
        poster= tasks2['poster'],
        state= tasks2['state'],
        genre= tasks2['genre']
                   )}

    def create(self, validated_data):
        return VideoObject(id=None, **validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance
