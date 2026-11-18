# -*- coding: utf-8 -*-
from odoo import models, fields


class SalonChair(models.Model):
    _name = 'salon.chair'
    _description = 'Fasilitas Kursi & Bed Salon'
    _order = 'sequence, name'

    name = fields.Char(string='Nama Fasilitas', required=True)
    sequence = fields.Integer(string='Urutan', default=10)
    resource_type = fields.Selection([
        ('hair_chair', 'Kursi Potong & Styling'),
        ('creambath_chair', 'Kursi Cuci & Creambath'),
        ('facial_bed', 'Bed Facial / Estetika'),
        ('nail_station', 'Meja Nail Art & Manicure'),
        ('laser_room', 'Ruang Tindakan Dokter / Laser'),
    ], string='Tipe Fasilitas', required=True, default='hair_chair')

    active = fields.Boolean(string='Aktif / Tersedia', default=True)
    notes = fields.Text(string='Keterangan Tambahan')
