# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SalonWarrantyClaim(models.Model):
    _name = 'salon.warranty.claim'
    _description = 'Klaim Garansi Retouch & Revisi Salon'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'claim_date desc, id desc'

    name = fields.Char(
        string='No. Klaim Retouch',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    appointment_id = fields.Many2one(
        'salon.appointment',
        string='Booking Sumber',
        required=True,
        tracking=True
    )
    partner_id = fields.Many2one(
        related='appointment_id.partner_id',
        string='Pelanggan',
        readonly=True
    )
    therapist_id = fields.Many2one(
        related='appointment_id.therapist_id',
        string='Terapis Asli',
        readonly=True
    )
    claim_date = fields.Date(
        string='Tanggal Pengajuan Retouch',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    complaint_type = fields.Selection([
        ('uneven_color', 'Warna Cat Rambut Tidak Merata'),
        ('nail_chipped', 'Nail Gel / Kutek Terkelupas Cepat'),
        ('haircut_adjustment', 'Potongan Rambut Perlu Penyesuaian'),
        ('skin_reaction', 'Iritasi Kulit Ringan Pasca Tindakan'),
    ], string='Jenis Keluhan', required=True, tracking=True)

    action_notes = fields.Text(
        string='Tindakan Koreksi yang Dilakukan'
    )
    is_free_charge = fields.Boolean(
        string='Gratis (Jaminan Mutu)',
        default=True,
        readonly=True
    )
    state = fields.Selection([
        ('draft', 'Pengajuan'),
        ('scheduled', 'Jadwal Retouch Ditetapkan'),
        ('done', 'Selesai Direvisi'),
        ('rejected', 'Ditolak'),
    ], default='draft', string='Status Retouch', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('salon.warranty.claim') or _('New')
        return super().create(vals_list)

    def action_schedule(self):
        for rec in self:
            rec.state = 'scheduled'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'
