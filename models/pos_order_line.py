from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    def _create_bom_inventory_moves(self):
        """Create inventory moves for BOM components"""
        self.ensure_one()
        
        if not (self.product_id.use_bom_in_pos and self.product_id.has_bom):
            return
        
        # Get BOM components
        bom_components = self.product_id.product_tmpl_id.get_bom_components()
        if not bom_components:
            return
        
        # Get the location for inventory moves
        location_src = self.order_id.session_id.config_id.picking_type_id.default_location_src_id
        location_dest = self.env['stock.location'].search([
            ('usage', '=', 'production'),
            ('company_id', '=', self.order_id.company_id.id)
        ], limit=1)
        
        if not location_dest:
            # Create a virtual production location if none exists
            location_dest = self.env['stock.location'].create({
                'name': 'POS BOM Production',
                'usage': 'production',
                'company_id': self.order_id.company_id.id,
                'location_id': self.env.ref('stock.stock_location_locations').id,
            })
        
        # Create stock moves for each BOM component
        for component in bom_components:
            component_product = self.env['product.product'].browse(component['product_id'])
            
            # Calculate the quantity needed based on order line qty
            component_qty = component['quantity'] * self.qty
            
            # Check if there's enough stock
            available_qty = component_product.with_context(
                location=location_src.id
            ).qty_available
            
            if available_qty < component_qty:
                raise ValidationError(
                    f"Not enough stock for component '{component['product_name']}'. "
                    f"Available: {available_qty}, Required: {component_qty}"
                )
            
            # Create stock move
            move_vals = {
                'name': f"POS BOM: {self.product_id.name} - {component['product_name']}",
                'product_id': component['product_id'],
                'product_uom': component['uom_id'],
                'product_uom_qty': component_qty,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
                'company_id': self.order_id.company_id.id,
                'state': 'draft',
                'origin': self.order_id.name,
                'date': fields.Datetime.now(),
                'picking_type_id': self._get_picking_type_id(),
            }
            
            move = self.env['stock.move'].create(move_vals)
            move._action_confirm()
            move._action_assign()
            move._action_done()
            
            # Force picking validation if the move has a picking and it's not done
            if move.picking_id and move.picking_id.state != 'done':
                try:
                    move.picking_id.button_validate()
                except Exception as e:
                    # Log the error but don't break the POS flow
                    self.env['ir.logging'].create({
                        'name': 'POS BOM Integration',
                        'type': 'server',
                        'level': 'WARNING',
                        'message': f'Could not auto-validate picking {move.picking_id.name}: {str(e)}',
                        'func': '_create_bom_inventory_moves',
                        'line': '1',
                    })
    
    def _get_picking_type_id(self):
        """Get the picking type for BOM moves"""
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('company_id', '=', self.order_id.company_id.id)
        ], limit=1)
        
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'outgoing'),
                ('company_id', '=', self.order_id.company_id.id)
            ], limit=1)
        
        return picking_type.id if picking_type else False
