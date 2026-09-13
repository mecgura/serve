"""
MecGuraServe - QR Code Generator
"""

import io
import segno
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

from tenants.models import RestaurantTable


def generate_qr_svg(qr_url, scale=10):
    """Generate QR code as SVG"""
    qr = segno.make(qr_url)
    buffer = io.BytesIO()
    qr.save(buffer, kind='svg', scale=scale, border=4)
    buffer.seek(0)
    return buffer.getvalue()


def generate_qr_png(qr_url, scale=10):
    """Generate QR code as PNG"""
    qr = segno.make(qr_url)
    buffer = io.BytesIO()
    qr.save(buffer, kind='png', scale=scale, border=4)
    buffer.seek(0)
    return buffer.getvalue()


def get_table_qr(request, table_id):
    """Get QR code for a specific table"""
    table = get_object_or_404(RestaurantTable, id=table_id)
    qr_url = table.qr_url
    
    format_type = request.GET.get('format', 'svg')
    
    if format_type == 'png':
        qr_data = generate_qr_png(qr_url)
        content_type = 'image/png'
        ext = 'png'
    else:
        qr_data = generate_qr_svg(qr_url)
        content_type = 'image/svg+xml'
        ext = 'svg'
    
    response = HttpResponse(qr_data, content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="table_{table.table_number}_qr.{ext}"'
    return response


@staff_member_required
def download_all_qr(request, tenant_slug):
    """Download all QR codes for a tenant"""
    from tenants.models import Tenant
    import zipfile
    
    tenant = get_object_or_404(Tenant, slug=tenant_slug)
    tables = RestaurantTable.objects.filter(tenant=tenant, is_active=True)
    
    # Create ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for table in tables:
            qr_data = generate_qr_png(table.qr_url, scale=15)
            filename = f"table_{table.table_number}_qr.png"
            zip_file.writestr(filename, qr_data)
    
    zip_buffer.seek(0)
    
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{tenant.slug}_qr_codes.zip"'
    return response
