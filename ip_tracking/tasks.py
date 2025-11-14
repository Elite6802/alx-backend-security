from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP

SENSITIVE_PATHS = ['/admin', '/login']
REQUEST_THRESHOLD = 100  # max requests per hour

@shared_task
def detect_suspicious_ips():
    """
    Detect IPs with >100 requests/hour or accessing sensitive paths.
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # Query recent requests
    recent_requests = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    # Count requests per IP
    ip_counts = {}
    for req in recent_requests:
        ip_counts[req.ip_address] = ip_counts.get(req.ip_address, 0) + 1

    # Flag IPs exceeding threshold
    for ip, count in ip_counts.items():
        if count > REQUEST_THRESHOLD:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                reason=f"{count} requests in the past hour"
            )

    # Flag IPs accessing sensitive paths
    sensitive_requests = recent_requests.filter(path__in=SENSITIVE_PATHS)
    for req in sensitive_requests:
        SuspiciousIP.objects.get_or_create(
            ip_address=req.ip_address,
            reason=f"Accessed sensitive path: {req.path}"
        )
