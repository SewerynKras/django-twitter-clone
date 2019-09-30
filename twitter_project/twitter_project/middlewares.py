from django.http import HttpResponseRedirect


class LoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            if getattr(view_func.view_class, 'login_required', True):
                return HttpResponseRedirect("/")
