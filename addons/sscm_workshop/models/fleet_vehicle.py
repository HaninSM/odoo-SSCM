# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    owner_id = fields.Many2one(
        'res.partner',
        string='Pemilik Kendaraan (Pelanggan)',
        required=True,
        tracking=True,
        help="Pelanggan pemilik kendaraan ini"
    )
    odometer_last = fields.Float(
        string='KM Terakhir',
        tracking=True,
        help="Odometer tercatat saat servis terakhir di bengkel"
    )
    service_order_ids = fields.One2many(
        'workshop.service.order',
        'vehicle_id',
        string='Riwayat Servis Bengkel'
    )
    service_count = fields.Integer(
        string='Total Servis',
        compute='_compute_service_count'
    )

    @api.depends('service_order_ids')
    def _compute_service_count(self):
        for vehicle in self:
            vehicle.service_count = len(vehicle.service_order_ids)

    def name_get(self):
        result = []
        for record in self:
            plate = record.license_plate or 'No Plate'
            model = record.model_id.name if record.model_id else ''
            name = f"[{plate}] {model} - {record.owner_id.name or ''}"
            result.append((record.id, name))
        return result
