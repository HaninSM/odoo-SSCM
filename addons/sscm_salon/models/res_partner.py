# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    treatment_history_ids = fields.One2many(
        'salon.treatment.history',
        'partner_id',
        string='Kartu Perawatan Estetika / Salon'
    )
    salon_appointment_ids = fields.One2many(
        'salon.appointment',
        'partner_id',
        string='Daftar Booking Salon'
    )
    salon_visit_count = fields.Integer(
        string='Total Kunjungan Perawatan',
        compute='_compute_salon_visit_count'
    )
    skin_hair_type = fields.Char(
        string='Tipe Kulit / Rambut',
        help="Contoh: Kulit Sensitif Berminyak, Rambut Kering Diwarnai"
    )
    known_allergies = fields.Text(
        string='Catatan Alergi Zat Kimiawi',
        help="Catatan alergi terhadap amonia, paraben, dll"
    )

    @api.depends('treatment_history_ids')
    def _compute_salon_visit_count(self):
        for partner in self:
            partner.salon_visit_count = len(partner.treatment_history_ids)
