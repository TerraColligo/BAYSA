from odoo import api, fields, models, _



class SaleLineCustom(models.Model):

    _inherit='sale.order.line'

    weight_new=fields.Float('Weight')

    @api.onchange('product_id')
    def _onchange_product_id_inherit(self):
        self.weight_new = self.product_id.weight


class SaleOrder(models.Model):

    _inherit='sale.order'


    total_weight = fields.Monetary(string='Total Weight', store=True, readonly=True, compute='_amount_all_weight',
                                     track_visibility='onchange')

    @api.depends('order_line.weight_new')
    def _amount_all_weight(self):

        for order in self:
            total_weight = 0.0
            for line in order.order_line:
                total_weight += line.weight_new*line.product_uom_qty

            order.update({
            'total_weight':total_weight
            })






