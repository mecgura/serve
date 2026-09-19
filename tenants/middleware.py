"""
MecGuraServe - Tenant Middleware
Identifies tenant from subdomain
"""

import ipaddress

from django.http import HttpResponseNotFound
from django.db import connection


class TenantMiddleware:
    """Identifies tenant from subdomain and sets request.tenant"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]

        try:
            ipaddress.ip_address(host)
            is_ip = True
        except ValueError:
            is_ip = False

        # Extract subdomain
        parts = host.split('.')

        # For localhost development, check for query param
        if is_ip or host in ['localhost', '127.0.0.1']:
            # Development mode - use ?tenant=slug in URL or session
            tenant_slug = request.GET.get('tenant') or request.session.get('tenant_slug')
            if tenant_slug:
                try:
                    from tenants.models import Tenant
                    request.tenant = Tenant.objects.get(slug=tenant_slug, is_active=True)
                    request.tenant_slug = tenant_slug
                except Tenant.DoesNotExist:
                    request.tenant = None
                    request.tenant_slug = None
            else:
                request.tenant = None
                request.tenant_slug = None
        elif len(parts) >= 3:
            # Production: subdomain.mecguraserve.com
            subdomain = parts[0]
            try:
                from tenants.models import Tenant
                request.tenant = Tenant.objects.get(slug=subdomain, is_active=True)
                request.tenant_slug = subdomain
            except Tenant.DoesNotExist:
                return HttpResponseNotFound("Resort not found")
        elif len(parts) == 2:
            # Main domain: mecguraserve.com
            request.tenant = None
            request.tenant_slug = None
        else:
            request.tenant = None
            request.tenant_slug = None

        response = self.get_response(request)
        return response
