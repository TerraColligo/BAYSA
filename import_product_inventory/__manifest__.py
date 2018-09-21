# -*- coding: utf-8 -*-

{'name': 'Import product in Batch odoo 11 EE',
 'version': '11.0.1.0.0',
 'category': 'other',
 'summary': 'With this module you can import product with product import batch',
 'depends': ['l10n_mx','l10n_mx_edi','sale_stock','purchase','point_of_sale'],
 'author': "Terra Colligo",
 'license': 'AGPL-3',
 'website': 'http://www.terracolligo.com/',
 'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/cron.xml',
        'views/product_import_batch_view.xml',
        'wizard/import_product_wizard_view.xml',
        'wizard/export_product_view.xml',
        ],
  "qweb": [
       "static/src/xml/base.xml",
        ],
 'installable': True,
 'application': True,
 }
