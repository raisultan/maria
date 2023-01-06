import re
from typing import Final
from django.core.cache import cache
from django.db.models import F
from django.http import HttpRequest
from ..models import Advert
class AdvertViewCountService:
    DEFAULT_IP: Final[str] = '127.0.0.1'
    FALLBACK_IP: Final[str] = '10.0.0.1'
    IP_REGEX: Final[str] = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

    VIEW_COUNT_CACHE_TEMPLATE: Final[str] = 'viewcount-{ip}-{user_agent}-{session_key}'
    REQUEST_SESSION_CACHE_LIFETIME: Final[int] = 60 * 60

    @classmethod
    def count(cls, request: HttpRequest, advert: Advert) -> None:
        request_cache_key = cls._compose_cache_key(request)
        request_cache_value = cache.get(request_cache_key)

        if not request_cache_value:
            Advert.objects.filter(id=advert.id).update(views=F('views') + 1)

            cache.set(
                key=request_cache_key,
                value=True,
                timeout=cls.REQUEST_SESSION_CACHE_LIFETIME,
            )
    @classmethod
    def _get_ip(cls, request: HttpRequest) -> str:
        ip_address = request.META.get(
            'HTTP_X_FORWARDED_FOR',
            request.META.get('REMOTE_ADDR', cls.DEFAULT_IP),
        )

        if ip_address:
            try:
                ip_address = cls.IP_REGEX.match(ip_address)
                if ip_address:
                    ip_address = ip_address.group(0)
                else:
                    ip_address = cls.FALLBACK_IP
            except IndexError:
                pass

        return ip_address
    @classmethod
    def _compose_cache_key(cls, request: HttpRequest) -> str:
        return cls.VIEW_COUNT_CACHE_TEMPLATE.format(
            ip=cls._get_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_key=request.session.session_key,
        )
