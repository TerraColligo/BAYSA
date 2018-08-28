from odoo import api, fields, models, _


class PurchaseOrderLineCustom(models.Model):

    _inherit='purchase.order.line'

    weight_po=fields.Float('Weight')

    @api.onchange('product_id')
    def _onchange_product_id_inherit_po(self):
        self.weight_po = self.product_id.weight



class PurchaseOrder(models.Model):

    _inherit='purchase.order'

    total_weight_po=fields.Monetary(string='Total Weight', store=True, readonly=True, compute='_amount_all_weight_po',
                                     track_visibility='onchange')

    @api.depends('order_line.weight_po')
    def _amount_all_weight_po(self):

        for order in self:
            total_weight_po = 0.0
            for line in order.order_line:
                total_weight_po += line.weight_po*line.product_qty

            order.update({
                'total_weight_po': total_weight_po
            })
