from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_bom = fields.Boolean(
        string='Has BOM',
        compute='_compute_has_bom',
        store=True,
        help='Indicates if this product has a Bill of Materials'
    )
    
    bom_ids = fields.One2many(
        'mrp.bom', 
        'product_tmpl_id', 
        string='Bills of Materials'
    )
    
    use_bom_in_pos = fields.Boolean(
        string='Use BOM in POS',
        default=False,
        help='When enabled, selling this product in POS will automatically deduct BOM components from inventory'
    )

    @api.depends('bom_ids')
    def _compute_has_bom(self):
        for record in self:
            record.has_bom = bool(record.bom_ids)

    def get_bom_components(self):
        """Get BOM components for this product"""
        self.ensure_one()
        if not self.bom_ids:
            return []
        
        # Get the first active BOM
        bom = self.bom_ids.filtered(lambda b: b.active)[:1]
        if not bom:
            return []
        
        components = []
        for line in bom.bom_line_ids:
            components.append({
                'product_id': line.product_id.id,
                'product_name': line.product_id.name,
                'quantity': line.product_qty,
                'uom_id': line.product_uom_id.id,
                'uom_name': line.product_uom_id.name,
            })
        return components
    
    def validate_bom_stock(self, quantity=1, pos_config=None):
        """Validate BOM component stock availability
        Returns dict with 'valid' boolean and 'error' message if invalid
        """
        self.ensure_one()
        
        # If not using BOM in POS, validation passes
        if not self.use_bom_in_pos or not self.has_bom:
            return {'valid': True}
        
        # Check if BOM validation is enabled in POS config
        if pos_config and hasattr(pos_config, 'enable_bom_validation') and not pos_config.enable_bom_validation:
            return {'valid': True}  # Validation disabled
        
        components = self.get_bom_components()
        if not components:
            return {'valid': True}
        
        # Check stock for each component
        for component in components:
            component_product = self.env['product.product'].browse(component['product_id'])
            required_qty = component['quantity'] * quantity
            available_qty = component_product.qty_available
            
            if available_qty < required_qty:
                return {
                    'valid': False,
                    'error': f"Not enough stock for BOM component '{component['product_name']}'. Available: {available_qty}, Required: {required_qty}",
                    'component_id': component['product_id'],
                    'component_name': component['product_name'],
                    'available': available_qty,
                    'required': required_qty
                }
        
        return {'valid': True}
