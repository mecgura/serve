"""
MecGuraServe - Context Processors
"""

from django.conf import settings


def tenant_context(request):
    """Add tenant info to all templates"""
    return {
        'tenant': getattr(request, 'tenant', None),
        'tenant_slug': getattr(request, 'tenant_slug', None),
        'brand_name': getattr(settings, 'BRAND_NAME', 'MecGuraServe'),
        'brand_domain': getattr(settings, 'BRAND_DOMAIN', 'mecguraserve.com'),
        'brand_tagline': getattr(settings, 'BRAND_TAGLINE', 'Scan. Order. Serve.'),
    }
