# -*- coding: utf-8 -*-
from openerp import api, exceptions, fields, models, _
from datetime import timedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_available = fields.Monetary(
        compute='_get_credit_used'
    )
    credit_expired = fields.Boolean(
        compute='_get_credit_used',
    )
    credit_ignore = fields.Boolean(
        default=False,
    )
    credit_used = fields.Monetary(
        compute='_get_credit_used',
    )
    credit_limit = fields.Monetary()
    grace_days = fields.Integer()
    expired_ignore = fields.Boolean(
        default=False,
    )
    sale_order_ignore = fields.Boolean(
        default=False,
    )

    @api.one
    def _get_credit_used(self):
        payment_term_credits = [payment for payment in self.env['account.payment.term'].search([(1, '=', 1)]) if payment.line_ids[0] and payment.line_ids[0].days > 0]
        payment_term_credits_ids = [p.id for p in payment_term_credits]
        invoices = self.env['account.invoice'].search([('partner_id', '=', self.id), ('state', '=', 'open'), ('payment_term_id', 'in', payment_term_credits_ids)])
        if not self.expired_ignore:
            self.credit_expired = False
            today = fields.Date.from_string(fields.Date.today())
            for invoice in invoices:
                date_due = fields.Date.from_string(invoice.date_due)
                if date_due + timedelta(days=self.grace_days) <= today:
                    self.credit_expired = True
        self.credit_available = self.credit_limit
        self.credit_used = 0
        if not self.sale_order_ignore:
            for sale in self.env['sale.order'].search([('partner_id', '=', self.id), ('state', '=', 'sale'), ('invoice_exist', '=', False)]):
                self.credit_used += sale.amount_total/sale.currency_id.rate
        if not self.credit_ignore:
            for invoice in invoices:
                self.credit_used += invoice.amount_total/invoice.currency_id.rate
        self.credit_available -= self.credit_used
