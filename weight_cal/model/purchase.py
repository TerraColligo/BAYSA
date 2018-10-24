from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.float_utils import float_is_zero, float_compare


class PurchaseOrderLineCustom(models.Model):

    _inherit='purchase.order.line'

    weight_po=fields.Float('Unit Weight',related='product_id.weight')

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

    @api.model
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'total_weight_stock':self.total_weight_po,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }

