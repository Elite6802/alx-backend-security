from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP
from ipware import get_client_ip
import requests
from django.core.cache import cache  # Django caching

GEOLOCATION_API_KEY = 'e184dbb925da412ca936301e28ca4360'
GEOLOCATION_API_URL = 'https://api.ipgeolocation.io/ipgeo'


class IPLoggingMiddleware(MiddlewareMixin):
    """
    Logs requests, blocks blacklisted IPs, and adds geolocation data.
    """

    def process_request(self, request):
        ip, is_routable = get_client_ip(request)
        if ip:
            # Block blacklisted IPs
            if BlockedIP.objects.filter(ip_address=ip).exists():
                return HttpResponseForbidden("Access denied.")

            # Try cache first
            geo_data = cache.get(f"geo_{ip}")
            if not geo_data:
                # Call the geolocation API
                try:
                    response = requests.get(GEOLOCATION_API_URL, params={
                        'apiKey': GEOLOCATION_API_KEY,
                        'ip': ip
                    }, timeout=5)
                    response.raise_for_status()
                    data = response.json()
                    geo_data = {
                        'country': data.get('country_name', ''),
                        'city': data.get('city', '')
                    }
                    # Cache for 24 hours (86400 seconds)
                    cache.set(f"geo_{ip}", geo_data, timeout=86400)
                except Exception:
                    geo_data = {'country': '', 'city': ''}

            # Log request with geolocation
            RequestLog.objects.create(
                ip_address=ip,
                path=request.path,
                country=geo_data['country'],
                city=geo_data['city']
            )
