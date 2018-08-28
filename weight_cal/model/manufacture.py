from odoo import api, fields, models, _


class MrpBomLine(models.Model):

    _inherit='mrp.bom.line'

    weight_bom=fields.Float('Weight')

    @api.onchange('product_id')
    def _onchange_product_id_inherit_bom(self):
        self.weight_bom = self.product_id.weight


class MrpBom(models.Model):

    _inherit='mrp.bom'

    total_weight_bom = fields.Monetary(string='Total Weight', store=True, readonly=True, compute='_amount_all_weight_bom',

                                       track_visibility='onchange', currency_field='company_currency_id')
    total_weight_bo=fields.Float('total weight')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
                                          readonly=True,
                                          help='Utility field to express amount currency', store=True)


    @api.depends('bom_line_ids.weight_bom')
    def _amount_all_weight_bom(self):
        for order in self:
            total_weight_bom = 0.0
            for line in order.bom_line_ids:
                total_weight_bom += line.weight_bom*line.product_qty

            order.update({
                'total_weight_bom': total_weight_bom,
                'total_weight_bo':total_weight_bom
            })


class ManufactureProduction(models.Model):

    _inherit='mrp.production'


    total_weight_mo_order=fields.Float('Total Weight',related='bom_id.total_weight_bo')
