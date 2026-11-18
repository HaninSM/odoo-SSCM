# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ServiceCommissionLine(models.Model):
    _name = 'service.commission.line'
    _description = 'Buku Besar Komisi & Insentif Karyawan'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='No. Referensi Komisi',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    source_reference = fields.Char(
        string='Dokumen Sumber',
        required=True,
        tracking=True,
        help="Nomor SPK Bengkel, Nomor Booking Salon, atau Nomor Invoice/POS Order"
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Karyawan Penerima',
        required=True,
        tracking=True,
        ondelete='restrict'
    )
    date = fields.Date(
        string='Tanggal Transaksi',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    commission_type = fields.Selection([
        ('service', 'Komisi Pengerjaan Jasa'),
        ('product_upsell', 'Insentif Penjualan Produk'),
        ('team_pool', 'Bagi Hasil Tim (Pool Carwash)'),
    ], string='Tipe Komisi', required=True, default='service', tracking=True)

    base_amount = fields.Monetary(
        string='Dasar Pengenaan Komisi (DPP)',
        required=True,
        currency_field='currency_id'
    )
    percentage = fields.Float(
        string='Persentase Komisi (%)',
        required=True
    )
    amount = fields.Monetary(
        string='Total Komisi',
        compute='_compute_amount',
        store=True,
        currency_field='currency_id',
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Mata Uang',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    notes = fields.Text(string='Catatan Tambahan')

    state = fields.Selection([
        ('accrued', 'Tercatat (Accrued)'),
        ('paid_in_payroll', 'Sudah Dibayarkan (Payroll)'),
        ('cancelled', 'Dibatalkan'),
    ], default='accrued', string='Status', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('service.commission.line') or _('New')
        return super().create(vals_list)

    @api.depends('base_amount', 'percentage')
    def _compute_amount(self):
        for record in self:
            record.amount = (record.base_amount * record.percentage) / 100.0

    def action_mark_paid_payroll(self):
        for record in self:
            if record.state != 'accrued':
                raise UserError(_("Hanya komisi berstatus Tercatat yang dapat dicairkan."))
            record.state = 'paid_in_payroll'

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
