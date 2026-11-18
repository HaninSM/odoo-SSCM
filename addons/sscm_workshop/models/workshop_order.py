# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class WorkshopServiceOrder(models.Model):
    _name = 'workshop.service.order'
    _description = 'Surat Perintah Kerja (SPK) Bengkel & Carwash'
    _order = 'create_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='No. SPK',
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
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Kendaraan',
        required=True,
        tracking=True,
        domain="[('owner_id', '=', partner_id)]"
    )
    odometer_in = fields.Float(
        string='Odometer Masuk (KM)',
        required=True,
        tracking=True
    )
    bay_id = fields.Many2one(
        'workshop.bay',
        string='Alokasi Pit / Bay',
        tracking=True
    )
    mechanic_id = fields.Many2one(
        'hr.employee',
        string='Mekanik Utama',
        tracking=True,
        domain="[('service_role', 'in', ['mechanic'])]"
    )
    washer_id = fields.Many2one(
        'hr.employee',
        string='Petugas Cuci / Detailing',
        tracking=True,
        domain="[('service_role', 'in', ['washer'])]"
    )
    date_entry = fields.Datetime(
        string='Waktu Masuk',
        default=fields.Datetime.now,
        required=True
    )
    date_done = fields.Datetime(
        string='Waktu Selesai',
        readonly=True
    )

    state = fields.Selection([
        ('draft', 'Draft / Booking'),
        ('queue', 'Antrean Pit'),
        ('in_progress', 'Sedang Dikerjakan'),
        ('qc', 'Quality Control'),
        ('carwash', 'Cuci & Detailing'),
        ('done', 'Selesai & Siap Bayar'),
        ('invoiced', 'Lunas / Selesai'),
        ('cancel', 'Dibatalkan'),
    ], default='draft', string='Status Antrean', tracking=True)

    complaint = fields.Text(string='Keluhan Pelanggan', tracking=True)
    diagnosis = fields.Text(string='Hasil Diagnosa Mekanik')

    service_line_ids = fields.One2many(
        'workshop.service.line',
        'order_id',
        string='Rincian Jasa Servis'
    )
    parts_line_ids = fields.One2many(
        'workshop.parts.line',
        'order_id',
        string='Suku Cadang & Oli'
    )

    amount_services = fields.Monetary(
        string='Total Jasa',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    amount_parts = fields.Monetary(
        string='Total Suku Cadang',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    amount_total = fields.Monetary(
        string='Total Tagihan',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Mata Uang',
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    # Garansi
    warranty_expiration_date = fields.Date(
        string='Garansi Servis Hingga (Tanggal)',
        compute='_compute_warranty_period',
        store=True
    )
    warranty_expiration_km = fields.Float(
        string='Garansi Servis Hingga (KM)',
        compute='_compute_warranty_period',
        store=True
    )
    warranty_claim_ids = fields.One2many(
        'workshop.warranty.claim',
        'original_order_id',
        string='Klaim Garansi Terkait'
    )

    # Invoicing
    invoice_id = fields.Many2one(
        'account.move',
        string='Faktur Penjualan',
        readonly=True,
        copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('workshop.service.order') or _('New')
        return super().create(vals_list)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.vehicle_id and self.vehicle_id.owner_id != self.partner_id:
            self.vehicle_id = False

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id and self.vehicle_id.odometer_last:
            self.odometer_in = self.vehicle_id.odometer_last

    @api.depends('service_line_ids.price_subtotal', 'parts_line_ids.price_subtotal')
    def _compute_totals(self):
        for order in self:
            order.amount_services = sum(order.service_line_ids.mapped('price_subtotal'))
            order.amount_parts = sum(order.parts_line_ids.mapped('price_subtotal'))
            order.amount_total = order.amount_services + order.amount_parts

    @api.depends('state', 'odometer_in', 'date_done')
    def _compute_warranty_period(self):
        for order in self:
            if order.state in ['done', 'invoiced'] and order.date_done:
                order.warranty_expiration_date = (order.date_done + timedelta(days=14)).date()
                order.warranty_expiration_km = order.odometer_in + 1000.0
            else:
                order.warranty_expiration_date = False
                order.warranty_expiration_km = 0.0

    def action_to_queue(self):
        for order in self:
            order.state = 'queue'

    def action_start_service(self):
        for order in self:
            if not order.bay_id:
                raise UserError(_("Pilih Pit/Bay terlebih dahulu sebelum memulai servis."))
            if order.bay_id.state == 'occupied' and order.bay_id.current_order_id != order:
                raise ValidationError(_("Pit/Bay %s sedang digunakan untuk SPK lain!", order.bay_id.name))
            
            order.bay_id.write({
                'state': 'occupied',
                'current_order_id': order.id
            })
            order.state = 'in_progress'

    def action_to_qc(self):
        for order in self:
            order.state = 'qc'

    def action_to_carwash(self):
        for order in self:
            order.state = 'carwash'

    def action_done(self):
        for order in self:
            order.date_done = fields.Datetime.now()
            # Update Odometer kendaraan terakhir
            if order.vehicle_id and order.odometer_in > (order.vehicle_id.odometer_last or 0):
                order.vehicle_id.odometer_last = order.odometer_in

            # Lepaskan Bay
            if order.bay_id:
                order.bay_id.write({
                    'state': 'available',
                    'current_order_id': False
                })

            # Buat entri komisi mekanik
            if order.mechanic_id and order.amount_services > 0:
                rate = order.mechanic_id.commission_rate_service or 15.0
                self.env['service.commission.line'].create({
                    'source_reference': order.name,
                    'employee_id': order.mechanic_id.id,
                    'commission_type': 'service',
                    'base_amount': order.amount_services,
                    'percentage': rate,
                    'notes': f"Komisi pengerjaan jasa SPK {order.name}"
                })

            # Buat insentif petugas cuci bila ada
            if order.washer_id:
                self.env['service.commission.line'].create({
                    'source_reference': order.name,
                    'employee_id': order.washer_id.id,
                    'commission_type': 'team_pool',
                    'base_amount': 25000.0,
                    'percentage': 100.0,
                    'notes': f"Insentif cuci mobil SPK {order.name}"
                })

            order.state = 'done'

    def action_create_invoice(self):
        for order in self:
            if order.invoice_id:
                raise UserError(_("Faktur untuk SPK ini sudah dibuat."))
            
            invoice_lines = []
            for s_line in order.service_line_ids:
                invoice_lines.append((0, 0, {
                    'product_id': s_line.product_id.id,
                    'name': s_line.name or s_line.product_id.display_name,
                    'quantity': s_line.qty,
                    'price_unit': s_line.price_unit,
                }))
            for p_line in order.parts_line_ids:
                invoice_lines.append((0, 0, {
                    'product_id': p_line.product_id.id,
                    'name': p_line.name or p_line.product_id.display_name,
                    'quantity': p_line.qty,
                    'price_unit': p_line.price_unit,
                }))

            move = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': order.partner_id.id,
                'ref': order.name,
                'invoice_date': fields.Date.context_today(self),
                'invoice_line_ids': invoice_lines,
            })
            order.invoice_id = move.id
            order.state = 'invoiced'
            return {
                'name': _('Faktur Penjualan'),
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': move.id,
                'type': 'ir.actions.act_window',
            }


class WorkshopServiceLine(models.Model):
    _name = 'workshop.service.line'
    _description = 'Baris Jasa Servis Bengkel'

    order_id = fields.Many2one('workshop.service.order', string='SPK Bengkel', ondelete='cascade', required=True)
    product_id = fields.Many2one('product.product', string='Paket / Jasa', domain=[('type', '=', 'service')], required=True)
    name = fields.Char(string='Deskripsi Pekerjaan')
    qty = fields.Float(string='Jumlah / Jam', default=1.0)
    price_unit = fields.Monetary(string='Tarif Jasa', currency_field='currency_id')
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='order_id.currency_id')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.price_unit = self.product_id.lst_price

    @api.depends('qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.qty * line.price_unit


class WorkshopPartsLine(models.Model):
    _name = 'workshop.parts.line'
    _description = 'Baris Suku Cadang Bengkel'

    order_id = fields.Many2one('workshop.service.order', string='SPK Bengkel', ondelete='cascade', required=True)
    product_id = fields.Many2one('product.product', string='Suku Cadang / Oli', domain=[('type', 'in', ['product', 'consu'])], required=True)
    name = fields.Char(string='Keterangan Part')
    qty = fields.Float(string='Kuantitas', default=1.0)
    price_unit = fields.Monetary(string='Harga Satuan', currency_field='currency_id')
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='order_id.currency_id')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.price_unit = self.product_id.lst_price

    @api.depends('qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.qty * line.price_unit
