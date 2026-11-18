# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    service_role = fields.Selection([
        ('mechanic', 'Mekanik / Teknisi'),
        ('washer', 'Petugas Cuci / Detailing'),
        ('therapist', 'Terapis / Beautician'),
        ('doctor', 'Dokter Estetika'),
        ('stylist', 'Hairstylist / Barber'),
    ], string='Peran Layanan', tracking=True)

    commission_rate_service = fields.Float(
        string='Komisi Jasa (%)',
        default=15.0,
        help="Persentase komisi standar untuk pengerjaan jasa perbaikan / treatment"
    )
    commission_rate_product = fields.Float(
        string='Komisi Produk Ritel (%)',
        default=5.0,
        help="Persentase komisi standar untuk penjualan produk pendukung (upselling)"
    )
    commission_line_ids = fields.One2many(
        'service.commission.line',
        'employee_id',
        string='Buku Besar Komisi'
    )
    total_accrued_commission = fields.Monetary(
        string='Total Komisi Akrual',
        compute='_compute_total_commission',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True
    )

    @api.depends('commission_line_ids.amount', 'commission_line_ids.state')
    def _compute_total_commission(self):
        for employee in self:
            accrued_lines = employee.commission_line_ids.filtered(lambda l: l.state == 'accrued')
            employee.total_accrued_commission = sum(accrued_lines.mapped('amount'))
