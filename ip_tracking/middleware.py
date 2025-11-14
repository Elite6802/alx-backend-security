from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP
from ipware import get_client_ip

class IPLoggingMiddleware(MiddlewareMixin):
    """
    Logs incoming requests and blocks IPs in the blacklist.
    """

    def process_request(self, request):
        ip, is_routable = get_client_ip(request)
        if ip:
            # Check if IP is blocked
            if BlockedIP.objects.filter(ip_address=ip).exists():
                return HttpResponseForbidden("Access denied.")

            # Log request
            RequestLog.objects.create(
                ip_address=ip,
                path=request.path
            )
