from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django_comments.forms import CommentForm
from notifications.signals import notify
from django_comments.models import Comment

from LinkGrabberDjango.models import FeatureRequest


class CommentFormWithTitle(CommentForm):

    def get_comment_create_data(self,**kwargs):
        # Use the data of the superclass, and add in the title field
        data = super(CommentFormWithTitle, self).get_comment_create_data()
        #print data
        featureReq = data["object_pk"]
        featureReq_type = ContentType.objects.get_for_model(FeatureRequest)
        #featureReq_model = featureReq_type.model_class()


        postedby = User.objects.get(username=data["user_name"])
        owneruser = FeatureRequest.objects.get(pk=featureReq).user
        if postedby == owneruser:
            notifyuser= User.objects.get(username="hennber")
        else:
            notifyuser = owneruser
        #print(notifyuser)
        notify.send(postedby,target=featureReq_type.get_object_for_this_type(pk=1), recipient=notifyuser, verb='you got a reply to a feature request.')
        return data
