# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_ignore = fields.Boolean(
        default=False,
    )
    credit_limit = fields.Monetary()
    expired_ignore = fields.Boolean(
        default=False,
    )
