# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'enterprise_task',
    'version': '1.1',
    'summary': 'weight on sale, Manufacture order',
    'sequence': 30,
    'description': """
    This Module Provides The functionality like you can get weight field in sale,
    purchase also in their report.
    """,
    'author': 'Planet-Odoo',
    'category': 'sale,manufacturing',
    'depends': ['base', 'sale', 'mrp','purchase'],
    'data': [
        'view/sale.xml',
        'view/purchase.xml',
        'view/product.xml',
        'view/manufacture.xml',
        'view/account_invoice.xml',
        'view/stock_picking.xml',
        'report/sale_order_report.xml',
        'report/purchase_quotation_report.xml',
        'report/purchase_order_report.xml',
        'report/account_invoice_report.xml',
        'report/stock_picking_report.xml',
        'report/Bom_report.xml',

    ],

    'installable': True,
    'application': False,
    'auto_install': False,

}
