from ratelimit.exceptions import Ratelimited
from django.utils.decorators import method_decorator

def custom_ratelimit(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            limit = '10/m'
        else:
            limit = '5/m'
        decorator = ratelimit(key='ip', rate=limit, method='GET', block=True)
        return decorator(view_func)(request, *args, **kwargs)
    return _wrapped_view

@custom_ratelimit
def login_view(request):
    if request.user.is_authenticated:
        return HttpResponse("You are already logged in.")
    return HttpResponse("Login page")
