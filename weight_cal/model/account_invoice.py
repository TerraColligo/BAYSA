from odoo import api, fields, models, _


class AccountInvoiceLine(models.Model):

    _inherit='account.invoice.line'

    weight_invoice=fields.Float('Unit Weight',related='product_id.weight')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    total_weight_invoice = fields.Float('Total Weight')
