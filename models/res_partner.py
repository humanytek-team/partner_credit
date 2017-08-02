from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_currency = fields.Many2one(
        'res.currency',
    )
    credit_ignore = fields.Boolean(
        default=False,
    )
    credit_limit = fields.Monetary(
        currency_field='credit_currency',
    )
