from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _process_bom_inventory_moves(self):
        """Process BOM inventory moves for all order lines"""
        for line in self.lines:
            if line.product_id.use_bom_in_pos and line.product_id.has_bom:
                line._create_bom_inventory_moves()

    def _create_order_picking(self):
        """Override to process BOM inventory moves"""
        res = super()._create_order_picking()
        self._process_bom_inventory_moves()
        return res

    @api.model
    def _order_fields(self, ui_order):
        """Add BOM information to order fields"""
        res = super()._order_fields(ui_order)
        
        # Process BOM lines if any
        if 'lines' in ui_order:
            for line_data in ui_order['lines']:
                if len(line_data) >= 3:  # [0, 0, line_dict]
                    line_dict = line_data[2]
                    if 'product_id' in line_dict:
                        product = self.env['product.product'].browse(line_dict['product_id'])
                        if product.use_bom_in_pos and product.has_bom:
                            line_dict['has_bom'] = True
                            line_dict['bom_components'] = product.product_tmpl_id.get_bom_components()
        
        return res
