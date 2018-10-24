from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError



class StockPicking(models.Model):
    _inherit='stock.picking'

    total_weight_stock = fields.Monetary(string='Total Weight', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)

class StockMove(models.Model):

    _inherit='stock.move.line'

    weight_stock_new=fields.Float('Unit Weight',related='product_id.weight')

