from django.http import HttpResponseRedirect


class LoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # meta graphics should not be login locked since these can
        # appear on the login page
        path = request.path_info
        if path.startswith("/meta/"):
            return None

        if not request.user.is_authenticated:
            if getattr(view_func.view_class, 'login_required', True):
                return HttpResponseRedirect("/")
