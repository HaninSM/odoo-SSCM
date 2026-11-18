# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class SalonAppointment(models.Model):
    _name = 'salon.appointment'
    _description = 'Booking & Sesi Perawatan Salon'
    _order = 'start_time desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='No. Booking',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Pelanggan',
        required=True,
        tracking=True
    )
    therapist_id = fields.Many2one(
        'hr.employee',
        string='Terapis / Stylist / Dokter',
        required=True,
        tracking=True,
        domain="[('service_role', 'in', ['therapist', 'doctor', 'stylist'])]"
    )
    chair_id = fields.Many2one(
        'salon.chair',
        string='Kursi / Bed Fasilitas',
        required=True,
        tracking=True
    )
    service_id = fields.Many2one(
        'product.product',
        string='Paket Layanan',
        domain=[('type', '=', 'service')],
        required=True,
        tracking=True
    )

    start_time = fields.Datetime(
        string='Waktu Mulai',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    end_time = fields.Datetime(
        string='Waktu Selesai',
        required=True,
        tracking=True
    )
    duration_minutes = fields.Integer(
        string='Durasi (Menit)',
        default=60
    )

    state = fields.Selection([
        ('draft', 'Draft Reservasi'),
        ('confirmed', 'Terkonfirmasi'),
        ('in_service', 'Sedang Perawatan'),
        ('done', 'Selesai'),
        ('cancel', 'Dibatalkan'),
    ], default='draft', string='Status Booking', tracking=True)

    price_unit = fields.Monetary(
        string='Biaya Layanan',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Mata Uang',
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    treatment_notes = fields.Text(
        string='Catatan Konsultasi / Formula Resep'
    )
    photo_before = fields.Binary(string='Foto Sebelum')
    photo_after = fields.Binary(string='Foto Sesudah')

    treatment_history_id = fields.Many2one(
        'salon.treatment.history',
        string='Rekam Medis/Kartu Perawatan',
        readonly=True
    )
    warranty_claim_ids = fields.One2many(
        'salon.warranty.claim',
        'appointment_id',
        string='Klaim Garansi Retouch'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('salon.appointment') or _('New')
        return super().create(vals_list)

    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.price_unit = self.service_id.lst_price
            if not self.end_time and self.start_time:
                self.end_time = self.start_time + timedelta(minutes=self.duration_minutes or 60)

    @api.onchange('start_time', 'duration_minutes')
    def _onchange_time_duration(self):
        if self.start_time and self.duration_minutes:
            self.end_time = self.start_time + timedelta(minutes=self.duration_minutes)

    @api.constrains('therapist_id', 'chair_id', 'start_time', 'end_time')
    def _check_conflicts(self):
        for record in self:
            if not (record.start_time and record.end_time):
                continue
            if record.end_time <= record.start_time:
                raise ValidationError(_("Waktu selesai harus lebih besar daripada waktu mulai."))

            domain = [
                ('id', '!=', record.id),
                ('state', 'in', ['confirmed', 'in_service']),
                ('start_time', '<', record.end_time),
                ('end_time', '>', record.start_time),
            ]
            # Validasi bentrok terapis
            if self.search(domain + [('therapist_id', '=', record.therapist_id.id)]):
                raise ValidationError(
                    _("Terapis %s telah memiliki jadwal lain pada rentang waktu tersebut!", record.therapist_id.name)
                )
            # Validasi bentrok kursi
            if self.search(domain + [('chair_id', '=', record.chair_id.id)]):
                raise ValidationError(
                    _("Kursi/Bed %s sedang digunakan untuk pelanggan lain pada rentang waktu tersebut!", record.chair_id.name)
                )

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'

    def action_start_service(self):
        for record in self:
            record.state = 'in_service'

    def action_done(self):
        for record in self:
            # 1. Buat catatan Treatment History otomatis
            history = self.env['salon.treatment.history'].create({
                'partner_id': record.partner_id.id,
                'appointment_id': record.id,
                'treatment_date': fields.Date.context_today(self),
                'therapist_id': record.therapist_id.id,
                'service_id': record.service_id.id,
                'formula_notes': record.treatment_notes,
                'photo_before': record.photo_before,
                'photo_after': record.photo_after,
            })
            record.treatment_history_id = history.id

            # 2. Buat catatan komisi terapis
            if record.therapist_id and record.price_unit > 0:
                rate = record.therapist_id.commission_rate_service or 15.0
                self.env['service.commission.line'].create({
                    'source_reference': record.name,
                    'employee_id': record.therapist_id.id,
                    'commission_type': 'service',
                    'base_amount': record.price_unit,
                    'percentage': rate,
                    'notes': f"Komisi treatment {record.service_id.name} ({record.name})"
                })

            record.state = 'done'

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'
