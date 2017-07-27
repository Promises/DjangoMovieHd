from django.utils import timezone


from .models import Profile


# class UpdateLastActivityMiddleware(object):
#     def process_view(self, request, view_func, view_args, view_kwargs):
#         assert hasattr(request, 'user'), 'The UpdateLastActivityMiddleware requires authentication middleware to be installed.'
#         if request.user.is_authenticated():
#             Profile.objects.filter(pk=request.user.id) \
#                            .update(last_activity=timezone.now())

class SimpleMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        if request.user.is_authenticated():
            Profile.objects.filter(pk=request.user.id).update(last_activity=timezone.now())
                # Code to be executed for each request/response after
        # the view is called.

        return response