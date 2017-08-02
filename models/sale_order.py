# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        for order in self:
            payment_term_credits = [payment for payment in self.env['account.payment.term'].search([(1, '=', 1)]) if payment.line_ids[0] and payment.line_ids[0].days > 0]
            if order.payment_term_id in payment_term_credits:
                if not order.partner_id.expired_ignore:
                    expired = self.env['account.invoice'].search([('partner_id', '=', order.partner_id.id), ('date_due', '<=', fields.Date.today()), ('state', 'not in', ['cancel', 'paid'])])
                    if expired and len(expired) > 0:
                        raise exceptions.Warning(_("¡POR EL MOMENTO NO SE PERMITE VENDER A CREDITO. EL CLIENTE TIENE SALDO VENCIDO EN FACTURAS ANTERIORES. PARA MAYOR INFORMACIÓN CONSULTAR EN CONTABILIDAD!"))
                if not order.partner_id.credit_ignore:
                    credit = order.amount_total*order.pricelist_id.currency_id.rate
                    for invoice in self.env['account.invoice'].search([('partner_id', '=', order.partner_id.id), ('date_due', '>', fields.Date.today()), ('state', 'not in', ['cancel', 'paid'])]):
                        credit += invoice.amount_total*invoice.currency_id.rate
                    if credit > order.partner_id.credit_limit:
                        raise exceptions.Warning(_("¡EL CLIENTE NO CUENTA CON CREDITO SUFICIENTE PARA ESTA VENTA, PARA MAYOR INFORMACIÓN CONSULTAR EN CONTABILIDAD!"))
        super(SaleOrder, self).action_confirm()
