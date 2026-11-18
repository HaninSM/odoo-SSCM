# -*- coding: utf-8 -*-
from odoo import models, fields


class SalonTreatmentHistory(models.Model):
    _name = 'salon.treatment.history'
    _description = 'Kartu Rekam Perawatan Estetika / Salon'
    _order = 'treatment_date desc, id desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Pelanggan',
        required=True,
        ondelete='cascade'
    )
    appointment_id = fields.Many2one(
        'salon.appointment',
        string='Sesi Booking Terkait',
        ondelete='set null'
    )
    treatment_date = fields.Date(
        string='Tanggal Perawatan',
        default=fields.Date.context_today,
        required=True
    )
    therapist_id = fields.Many2one(
        'hr.employee',
        string='Terapis / Stylist / Dokter'
    )
    service_id = fields.Many2one(
        'product.product',
        string='Layanan Diterima'
    )

    formula_notes = fields.Text(
        string='Resep Formula & Catatan Khusus',
        help="Contoh: Pewarna No. 7.1 (30g) + 9% (45g), reaksi alergi ringan, dsb"
    )
    skin_hair_condition = fields.Text(
        string='Kondisi Kulit / Rambut Saat Datang'
    )
    photo_before = fields.Binary(string='Foto Sebelum')
    photo_after = fields.Binary(string='Foto Sesudah')
