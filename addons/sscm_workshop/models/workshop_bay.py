# -*- coding: utf-8 -*-
from odoo import models, fields


class WorkshopBay(models.Model):
    _name = 'workshop.bay'
    _description = 'Workcenter Bay / Pit Bengkel & Carwash'
    _order = 'sequence, name'

    name = fields.Char(string='Nama Bay / Pit', required=True)
    sequence = fields.Integer(string='Urutan', default=10)
    bay_type = fields.Selection([
        ('general_repair', 'Pit Servis Umum / Ringan'),
        ('heavy_repair', 'Pit Servis Berat / Turun Mesin'),
        ('spooring', 'Pit Spooring & Balancing'),
        ('carwash', 'Bay Cuci & Detailing'),
    ], string='Tipe Bay', required=True, default='general_repair')

    state = fields.Selection([
        ('available', 'Tersedia'),
        ('occupied', 'Sedang Digunakan'),
        ('maintenance', 'Dalam Perawatan / Rusak'),
    ], default='available', string='Status Bay', tracking=True)

    current_order_id = fields.Many2one(
        'workshop.service.order',
        string='Order yang Sedang Berjalan',
        readonly=True
    )
    notes = fields.Text(string='Spesifikasi Peralatan (Kapasitas Ton, Lift Type, dll)')
