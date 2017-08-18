# -*- coding: utf-8 -*-
from openerp import api, exceptions, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        payment_term_credits = [payment for payment in self.env['account.payment.term'].search([(1, '=', 1)]) if payment.line_ids and payment.line_ids[0].days > 0]
        for order in self:
            if order.payment_term in payment_term_credits:
                if not order.partner_id.expired_ignore and order.partner_id.credit_expired:
                    raise exceptions.Warning(_("¡POR EL MOMENTO NO SE PERMITE VENDER A CRÉDITO. EL CLIENTE TIENE SALDO VENCIDO EN FACTURAS ANTERIORES. PARA MAYOR INFORMACIÓN CONSULTAR EN CONTABILIDAD!"))
                if not order.partner_id.credit_ignore:
                    if order.partner_id.credit_used + order.amount_total/order.pricelist_id.currency_id.rate > order.partner_id.credit_limit:
                        raise exceptions.Warning(_("¡EL CLIENTE NO CUENTA CON CRÉDITO SUFICIENTE PARA ESTA VENTA, PARA MAYOR INFORMACIÓN CONSULTAR EN CONTABILIDAD!"))
        super(SaleOrder, self).action_button_confirm()
