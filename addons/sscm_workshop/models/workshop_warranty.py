# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WorkshopWarrantyClaim(models.Model):
    _name = 'workshop.warranty.claim'
    _description = 'Klaim Garansi Servis Bengkel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'claim_date desc, id desc'

    name = fields.Char(
        string='No. Klaim Garansi',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    original_order_id = fields.Many2one(
        'workshop.service.order',
        string='SPK Sumber',
        required=True,
        tracking=True
    )
    vehicle_id = fields.Many2one(
        related='original_order_id.vehicle_id',
        string='Kendaraan',
        readonly=True
    )
    partner_id = fields.Many2one(
        related='original_order_id.partner_id',
        string='Pelanggan',
        readonly=True
    )
    claim_date = fields.Date(
        string='Tanggal Pengajuan Klaim',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    odometer_claim = fields.Float(
        string='Odometer Saat Klaim (KM)',
        required=True,
        tracking=True
    )
    claim_reason = fields.Text(
        string='Keluhan / Kerusakan Lanjutan',
        required=True,
        tracking=True
    )
    investigation_notes = fields.Text(
        string='Catatan Pemeriksaan Teknisi'
    )

    is_within_time_warranty = fields.Boolean(
        string='Masih Dalam Waktu Garansi',
        compute='_compute_warranty_validity'
    )
    is_within_km_warranty = fields.Boolean(
        string='Masih Dalam Batas KM Garansi',
        compute='_compute_warranty_validity'
    )
    is_warranty_valid = fields.Boolean(
        string='Garansi Valid & Berlaku',
        compute='_compute_warranty_validity'
    )

    action_taken = fields.Selection([
        ('free_repair', 'Servis Ulang Gratis (Rp 0 ke Pelanggan)'),
        ('supplier_claim', 'Retur Suku Cadang ke Supplier (Cacat Pabrik)'),
        ('rejected', 'Klaim Ditolak (Di luar syarat garansi)'),
    ], string='Tindakan Klaim', tracking=True)

    state = fields.Selection([
        ('draft', 'Pengajuan Baru'),
        ('investigation', 'Pemeriksaan Teknisi'),
        ('approved', 'Disetujui'),
        ('done', 'Selesai Dikerjakan'),
        ('rejected', 'Ditolak'),
    ], default='draft', string='Status Klaim', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('workshop.warranty.claim') or _('New')
        return super().create(vals_list)

    @api.depends('original_order_id', 'claim_date', 'odometer_claim')
    def _compute_warranty_validity(self):
        for claim in self:
            order = claim.original_order_id
            if order and order.warranty_expiration_date:
                claim.is_within_time_warranty = claim.claim_date <= order.warranty_expiration_date
                claim.is_within_km_warranty = claim.odometer_claim <= order.warranty_expiration_km
                claim.is_warranty_valid = claim.is_within_time_warranty and claim.is_within_km_warranty
            else:
                claim.is_within_time_warranty = False
                claim.is_within_km_warranty = False
                claim.is_warranty_valid = False

    def action_investigate(self):
        for claim in self:
            claim.state = 'investigation'

    def action_approve(self):
        for claim in self:
            claim.state = 'approved'

    def action_done(self):
        for claim in self:
            claim.state = 'done'

    def action_reject(self):
        for claim in self:
            claim.state = 'rejected'
