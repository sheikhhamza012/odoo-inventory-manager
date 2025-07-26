from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _get_pos_ui_product_product(self, params):
        """Override to include BOM fields in POS product data"""
        result = super()._get_pos_ui_product_product(params)
        
        # Add BOM fields to each product
        product_ids = [product['id'] for product in result]
        products = self.env['product.product'].browse(product_ids)
        
        # Create a mapping of product ID to BOM data
        bom_data = {}
        bom_products_count = 0
        for product in products:
            template = product.product_tmpl_id
            use_bom = template.use_bom_in_pos
            has_bom = template.has_bom
            
            bom_data[product.id] = {
                'use_bom_in_pos': use_bom,
                'has_bom': has_bom,
            }
            
            if use_bom and has_bom:
                bom_products_count += 1
                _logger.info(f"BOM Product found: {product.name} (ID: {product.id}) - use_bom_in_pos: {use_bom}, has_bom: {has_bom}")
        
        # Add BOM data to result
        for product_data in result:
            product_id = product_data['id']
            if product_id in bom_data:
                product_data.update(bom_data[product_id])
                
        _logger.info(f"Loaded {len(result)} products with BOM data, {bom_products_count} BOM products found")
        return result


class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    enable_bom_validation = fields.Boolean(
        string='Enable BOM Stock Validation',
        default=True,
        help='When enabled, POS will validate BOM component stock before allowing orders'
    )
