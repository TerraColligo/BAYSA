# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'enterprise_task',
    'version': '1.1',
    'summary': 'weight on sale, Manufacture order',
    'sequence': 30,
    'description': """
    
    """,
    'author': 'Planet-Odoo',
    'category': 'sale,manufacturing',
    'depends': ['base', 'sale', 'mrp','purchase'],
    'data': [
        'view/sale.xml',
        'view/purchase.xml',
        'view/manufacture.xml',

    ],

    'installable': True,
    'application': False,
    'auto_install': False,

}
