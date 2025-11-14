from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog
from ipware import get_client_ip

class IPLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip, is_routable = get_client_ip(request)
        if ip:
            RequestLog.objects.create(
                ip_address=ip,
                path=request.path
            )
