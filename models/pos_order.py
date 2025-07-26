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
    def create_from_ui(self, orders, draft=False):
        """Override to validate BOM stock before creating orders"""
        # Validate BOM stock for all orders before creation
        for order_data in orders:
            if 'data' in order_data:
                self._validate_order_bom_stock_from_ui(order_data['data'])
        
        return super().create_from_ui(orders, draft)
    
    @api.model
    def _validate_order_bom_stock_from_ui(self, order_data):
        """Validate BOM stock from UI order data"""
        if 'lines' not in order_data:
            return
        
        for line_data in order_data['lines']:
            if len(line_data) >= 3:  # [0, 0, line_dict]
                line_dict = line_data[2]
                if 'product_id' in line_dict and 'qty' in line_dict:
                    product = self.env['product.product'].browse(line_dict['product_id'])
                    if product.use_bom_in_pos and product.has_bom:
                        validation = product.product_tmpl_id.validate_bom_stock(line_dict['qty'])
                        if not validation['valid']:
                            raise ValidationError(
                                f"Order validation failed: {validation['error']}"
                            )

    @api.model
    def validate_bom_stock_rpc(self, product_id, quantity, pos_config_id=None):
        """RPC method to validate BOM stock from frontend
        Args:
            product_id: ID of the product to validate
            quantity: Quantity being ordered
            pos_config_id: ID of the POS config (optional)
        Returns:
            dict: {'valid': bool, 'error': str, 'details': dict}
        """
        try:
            product = self.env['product.product'].browse(product_id)
            if not product.exists():
                return {'valid': False, 'error': 'Product not found'}
            
            pos_config = None
            if pos_config_id:
                pos_config = self.env['pos.config'].browse(pos_config_id)
            
            validation = product.product_tmpl_id.validate_bom_stock(quantity, pos_config)
            return validation
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def validate_order_bom_stock(self):
        """Validate BOM stock for all order lines
        Returns dict with validation results
        """
        self.ensure_one()
        errors = []
        
        for line in self.lines:
            if line.product_id.use_bom_in_pos and line.product_id.has_bom:
                validation = line.product_id.product_tmpl_id.validate_bom_stock(line.qty)
                if not validation['valid']:
                    errors.append({
                        'line_id': line.id,
                        'product_name': line.product_id.name,
                        'quantity': line.qty,
                        'error': validation['error'],
                        'details': validation
                    })
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
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
