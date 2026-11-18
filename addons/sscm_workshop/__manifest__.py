# -*- coding: utf-8 -*-
{
    'name': 'SSCM Workshop & Carwash Management',
    'version': '17.0.1.0.0',
    'category': 'Services/Automotive',
    'summary': 'Manajemen Antrean Pit/Bay, Rekam Kendaraan Pelanggan, Garansi Servis, & Komisi Bengkel',
    'description': """
SSCM Workshop & Carwash
=======================
Modul Service Supply Chain Management untuk Bengkel Kendaraan dan Carwash:
- Antrean Servis visual Kanban berbasis Bay / Pit / Lift Servis
- Catatan Kendaraan Pelanggan (Plat Nomor, Odometer KM, Riwayat Servis & Part)
- Konsumsi Suku Cadang & Oli terhubung ke stok gudang Odoo
- Garansi Servis (Masa berlaku 14 hari / 1.000 KM & klaim garansi Rp 0)
- Integrasi komisi mekanik dan insentif cuci mobil
    """,
    'author': 'HaninSM',
    'website': 'https://github.com/HaninSM/odoo-SSCM',
    'depends': [
        'base',
        'mail',
        'fleet',
        'stock',
        'account',
        'sscm_core',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/bay_data.xml',
        'views/workshop_bay_views.xml',
        'views/workshop_order_views.xml',
        'views/workshop_warranty_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
