# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        payment_term_credits = [payment for payment in self.env['account.payment.term'].search([(1, '=', 1)]) if payment.line_ids[0] and payment.line_ids[0].days > 0]
        payment_term_credits_ids = [p.id for p in payment_term_credits]
        for order in self:
            if order.payment_term_id in payment_term_credits:
                invoices = self.env['account.invoice'].search([('partner_id', '=', order.partner_id.id), ('state', '=', 'open'), ('payment_term_id', 'in', payment_term_credits_ids)])
                if not order.partner_id.expired_ignore:
                    for invoice in invoices:
                        if invoice.date_due <= fields.Date.today():
                            raise exceptions.Warning(_("¡POR EL MOMENTO NO SE PERMITE VENDER A CRÉDITO. EL CLIENTE TIENE SALDO VENCIDO EN FACTURAS ANTERIORES. PARA MAYOR INFORMACIÓN CONSULTAR EN CONTABILIDAD!"))
                if not order.partner_id.credit_ignore:
                    credit = order.amount_total*order.pricelist_id.currency_id.rate
                    for invoice in invoices:
                        credit += invoice.amount_total*invoice.currency_id.rate
                    if credit > order.partner_id.credit_limit:
                        raise exceptions.Warning(_("¡EL CLIENTE NO CUENTA CON CRÉDITO SUFICIENTE PARA ESTA VENTA, PARA MAYOR INFORMACIÓN CONSULTAR EN CONTABILIDAD!"))
        super(SaleOrder, self).action_confirm()
