# -*- coding: utf-8 -*-
{
    'name': 'SSCM Salon & Beauty Clinic Management',
    'version': '17.0.1.0.0',
    'category': 'Services/Beauty',
    'summary': 'Booking Kursi & Terapis, Kartu Perawatan E-Medical, Garansi Retouch, & Analisa Layanan Terlaris',
    'description': """
SSCM Salon & Beauty Clinic
==========================
Modul Service Supply Chain Management untuk Salon, Barbershop, dan Klinik Kecantikan:
- Dual-Resource Booking (Alokasi Kursi/Bed dan Staf Terapis dengan pencegahan jadwal bentrok)
- Kartu Perawatan Pelanggan (Treatment History, formula racikan pewarna/obat, foto before-after)
- Garansi Retouch / Perbaikan pengerjaan dalam 7 hari (Rp 0 ke pelanggan)
- Pengurangan otomatis bahan habis pakai berbasis BOM Kit
- Perhitungan komisi pengerjaan jasa terapis dan insentif produk skincare
- Laporan Analisa Layanan Terlaris (Pivot & Graph BI)
    """,
    'author': 'HaninSM',
    'website': 'https://github.com/HaninSM/odoo-SSCM',
    'depends': [
        'base',
        'mail',
        'product',
        'point_of_sale',
        'sscm_core',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/chair_data.xml',
        'views/salon_chair_views.xml',
        'views/salon_appointment_views.xml',
        'views/salon_treatment_history_views.xml',
        'views/salon_warranty_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
