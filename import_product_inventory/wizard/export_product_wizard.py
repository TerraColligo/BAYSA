# -*- coding: utf-8 -*-
from odoo import models,api,fields
from odoo.exceptions import Warning
from datetime import datetime

import uuid
import io
from odoo.tools.misc import xlwt
from itertools import product
import base64

class export_product_with_inventory_file(models.TransientModel):
    _name ='export.product.with.inventory.file'

    file_data = fields.Binary("File Data")

    @api.multi
    def export_products(self):
        filename = 'products_%s.xls'%(datetime.today().strftime("%Y_%m_%d_%H_%M_%S"))
        workbook = xlwt.Workbook()
        bold = xlwt.easyxf("font: bold on;") # "cell_locked true" is default

        quant_obj = self.env['stock.quant']
        products = self.env['product.product'].search([])
        company_id = self.env.user.company_id.id

        #worksheet = workbook.add_worksheet('Products')
        worksheet = workbook.add_sheet('Products')
        worksheet.protect = True
        
        editable = xlwt.easyxf("protection: cell_locked false;")
        
        headers = ['id','categ_id/name','pos_categ_id/name','available_in_pos','name','barcode','default_code','unit_of_measurement','uom_po_id','weight','l10n_mx_edi_code_sat_id','supplier_taxes_id','taxes_id','type','route_ids/id','purchase_ok','sale_ok','standard_price','lst_price','seller_ids/name/name']
        warehouse_ids = []
        location_ids = []
        wh_location_ids = []
        product_obj = self.env['product.product']
        product_ids = products.ids
        product_inventory_by_wh = {}
        product_inventory_by_location = {}
        for warehouse in self.env['stock.warehouse'].search([('company_id','=',company_id)]):
            headers.append('[WH]'+warehouse.code)
            #For faster quantity calculation, used quary.
            domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_obj._get_domain_locations_new([warehouse.lot_stock_id.id])
            domain_quant = [('product_id', 'in', product_ids)] + domain_quant_loc
            query = quant_obj._where_calc(domain_quant)
            from_clause, where_clause, where_clause_params = query.get_sql()
            where_str = where_clause and (" WHERE %s" % where_clause) or ''

            query_str = 'SELECT product_id, sum(quantity) as quantity FROM '+ from_clause + where_str + ' group by product_id'
            self._cr.execute(query_str, where_clause_params)
            res = dict(self._cr.fetchall())
            product_inventory_by_wh.update({warehouse.id:res})
            warehouse_ids.append(warehouse.id)
            wh_location_ids.append(warehouse.lot_stock_id)
            
        for location in self.env['stock.location'].search([('company_id','=',company_id), ('usage', '=', 'internal')]):
            if location.id in wh_location_ids:
                continue
            headers.append('[LOC]'+location.display_name)
            #For faster quantity calculation, used quary.
            domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_obj._get_domain_locations_new([location.id])
            domain_quant = [('product_id', 'in', product_ids)] + domain_quant_loc
            query = quant_obj._where_calc(domain_quant)
            from_clause, where_clause, where_clause_params = query.get_sql()
            where_str = where_clause and (" WHERE %s" % where_clause) or ''

            query_str = 'SELECT product_id, sum(quantity) as quantity FROM '+ from_clause + where_str + ' group by product_id'
            self._cr.execute(query_str, where_clause_params)
            res = dict(self._cr.fetchall())
            product_inventory_by_location.update({location.id:res})
            location_ids.append(location.id)

        product_xml_ids = dict(self.__ensure_xml_id_custom(products))
        sellers_mapping_dict = {}
        for i,header in enumerate(headers):
            worksheet.write(0, i, header, bold)
            worksheet.col(i).width = 8000 # around 220 pixels

        def splittor(rs):
            """ Splits the self recordset in batches of 1000 (to avoid
            entire-recordset-prefetch-effects) & removes the previous batch
            from the cache after it's been iterated in full
            """
            for idx in range(0, len(rs), 1000):
                sub = rs[idx:idx+1000]
                for rec in sub:
                    yield rec
                rs.invalidate_cache(ids=sub.ids)
        row_index = 1
        pos_installed = hasattr(self.env['product.product'], 'available_in_pos')
        for product in splittor(products):
            if product.route_ids:
                xml_ids = [xid for _, xid in self.__ensure_xml_id_custom(product.route_ids)]
                route_ids = ','.join(xml_ids) or False
            else:
                route_ids=''
            if product.supplier_taxes_id:
                # xml_ids = [xid for _, xid in self.__ensure_xml_id_custom(product.supplier_taxes_id)]
                # supplier_taxes_ids = ','.join(xml_ids) or False
                supplier_taxes_ids = ','.join([tax.name for tax in product.supplier_taxes_id])
            else:
                supplier_taxes_ids = ''
            if product.taxes_id:
                # xml_ids = [xid for _, xid in self.__ensure_xml_id_custom(product.taxes_id)]
                # customer_taxes_ids = ','.join(xml_ids) or False
                customer_taxes_ids = ','.join([tax.name for tax in product.taxes_id])
            else:
                customer_taxes_ids = ''
            if product.l10n_mx_edi_code_sat_id:
                xml_ids = [xid for _, xid in self.__ensure_xml_id_custom(product.l10n_mx_edi_code_sat_id)]
                l10n_mx_edi_code_sat_id = ','.join(xml_ids) or False
            else:
                l10n_mx_edi_code_sat_id = ''
            i=0
            worksheet.write(row_index, i, product_xml_ids.get(product.id),editable)
            i +=1
            worksheet.write(row_index, i, product.categ_id.complete_name, editable)
            i +=1
            #########
            if pos_installed:
                worksheet.write(row_index, i, product.pos_categ_id.complete_categ_name or None, editable)
                i +=1
                worksheet.write(row_index, i, 1 if product.available_in_pos else 0, editable)
                i +=1
            else:
                worksheet.write(row_index, i, None, editable)
                i +=1
                worksheet.write(row_index, i, None, editable)
                i +=1
            #########
            worksheet.write(row_index, i, product.name, editable)
            i +=1
            worksheet.write(row_index, i, product.barcode or '', editable)
            i +=1
            worksheet.write(row_index, i, product.default_code or '', editable)
            i +=1
            worksheet.write(row_index, i, product.uom_id.name, editable)
            i +=1
            worksheet.write(row_index, i, product.uom_po_id.name, editable)
            i +=1
            worksheet.write(row_index, i, product.weight or 0.0, editable)
            i +=1
            worksheet.write(row_index, i, product.l10n_mx_edi_code_sat_id.code, editable)
            i +=1
            worksheet.write(row_index, i, supplier_taxes_ids, editable)
            i +=1
            worksheet.write(row_index, i, customer_taxes_ids, editable)
            i +=1
            worksheet.write(row_index, i, product.type, editable)
            i +=1
            worksheet.write(row_index, i, route_ids, editable)
            i +=1
            worksheet.write(row_index, i, product.purchase_ok, editable)
            i +=1
            worksheet.write(row_index, i, product.sale_ok, editable)
            i +=1
            worksheet.write(row_index, i, product.standard_price, editable)
            i +=1
            worksheet.write(row_index, i, product.lst_price, editable)
            i +=1
            seller_xml_ids = []
            for seller in product.seller_ids.mapped('name'):
                if seller.id not in sellers_mapping_dict:
                    xml_rec = self.__ensure_xml_id_custom(seller)
                    if xml_rec:
                        sellers_mapping_dict.update({seller.id: xml_rec and xml_rec[0][1] or False})
                seller_xml_ids.append(sellers_mapping_dict.get(seller.id) or '')

            worksheet.write(row_index, i, ','.join(seller_xml_ids), editable)
            i +=1

            for warehouse_id in warehouse_ids:
                worksheet.write(row_index, i, product_inventory_by_wh[warehouse_id].get(product.id,0.0), editable)
                #worksheet.write(row_index, i, product.with_context(warehouse=warehouse_id).qty_available)
                i +=1
            
            for location_id in location_ids:
                worksheet.write(row_index, i, product_inventory_by_location[location_id].get(product.id,0.0), editable)
                #worksheet.write(row_index, i, product.with_context(warehouse=warehouse_id).qty_available)
                i +=1
            row_index += 1
        for i in range(row_index,row_index+5000):
            for h,header in enumerate(headers): 
                worksheet.write(row_index, h, None, editable)
            row_index += 1
#         workbook.close()
#         fp.seek(0)
#         data = fp.read()
#         fp.close()

        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()

        self.write({'file_data':base64.b64encode(data)})
        return {
            'type' : 'ir.actions.act_url',
            'url':   '/web/binary/savefile_custom?model=%s&field=file_data&id=%s&file_name=%s&content_type="application/vnd.ms-excel"' % (self._name, self.id,filename),
            'target':'self',
            }

    def __ensure_xml_id_custom(self, records):
        """ Create missing external ids for records in ``self``, and return an
            iterator of pairs ``(record, xmlid)`` for the records in ``self``.

        :rtype: Iterable[Model, str | None]
        """

        if not records:
            return iter([])
        modname = '__export__'

        cr = self.env.cr
        cr.execute("""
            SELECT res_id, CASE WHEN length(module)>0 THEN module || '.' || name ELSE name END AS external_id
            FROM ir_model_data
            WHERE model = %s AND res_id in %s
        """, (records._name, tuple(records.ids)))

        result = cr.fetchall()
        if len(result)==len(records):
            return result

        cr.execute("""
            SELECT res_id, module, name
            FROM ir_model_data
            WHERE model = %s AND res_id in %s
        """, (records._name, tuple(records.ids)))
        xids = {
            res_id: (module, name)
            for res_id, module, name in cr.fetchall()
        }
        def to_xid(record_id):
            (module, name) = xids[record_id]
            return ('%s.%s' % (module, name)) if module else name

        # create missing xml ids
        missing = records.filtered(lambda r: r.id not in xids)
        if not missing:
            return (
                (record.id, to_xid(record.id))
                for record in records
            )
        xids.update(
            (r.id, (modname, '%s_%s_%s' % (
                r._table,
                r.id,
                uuid.uuid4().hex[:8],
            )))
            for r in missing
        )
        fields = ['module', 'model', 'name', 'res_id']
        cr.copy_from(io.StringIO(
            u'\n'.join(
                u"%s\t%s\t%s\t%d" % (
                    modname,
                    record._name,
                    xids[record.id][1],
                    record.id,
                )
                for record in missing
            )),
            table='ir_model_data',
            columns=fields,
        )
        self.env['ir.model.data'].invalidate_cache(fnames=fields)

        return (
            (record.id, to_xid(record.id))
            for record in records
        )