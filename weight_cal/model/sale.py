from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError



class SaleLineCustom(models.Model):

    _inherit='sale.order.line'

    weight_new=fields.Float('Unit Weight',related='product_id.weight')


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

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'total_weight_invoice':self.total_weight,
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id
        }
        return invoice_vals






