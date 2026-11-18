# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vehicle_ids = fields.One2many(
        'fleet.vehicle',
        'owner_id',
        string='Kendaraan Pelanggan'
    )
    vehicle_count = fields.Integer(
        string='Jumlah Kendaraan',
        compute='_compute_vehicle_count'
    )
    workshop_order_ids = fields.One2many(
        'workshop.service.order',
        'partner_id',
        string='Riwayat Servis'
    )
    workshop_order_count = fields.Integer(
        string='Total Servis Bengkel',
        compute='_compute_workshop_order_count'
    )

    @api.depends('vehicle_ids')
    def _compute_vehicle_count(self):
        for partner in self:
            partner.vehicle_count = len(partner.vehicle_ids)

    @api.depends('workshop_order_ids')
    def _compute_workshop_order_count(self):
        for partner in self:
            partner.workshop_order_count = len(partner.workshop_order_ids)
