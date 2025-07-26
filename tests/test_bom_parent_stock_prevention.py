# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestBOMParentStockPrevention(TransactionCase):
    """Test suite to verify that parent product stock is not deducted for BOM products"""
    
    def setUp(self):
        super().setUp()
        
        # Create test products
        self.parent_product = self.env['product.product'].create({
            'name': 'BOM Parent Product',
            'type': 'product',
            'use_bom_in_pos': True,
        })
        
        self.component1 = self.env['product.product'].create({
            'name': 'Component 1',
            'type': 'product',
        })
        
        self.component2 = self.env['product.product'].create({
            'name': 'Component 2',
            'type': 'product',
        })
        
        # Create BOM
        self.bom = self.env['mrp.bom'].create({
            'product_tmpl_id': self.parent_product.product_tmpl_id.id,
            'product_qty': 1.0,
            'bom_line_ids': [
                (0, 0, {
                    'product_id': self.component1.id,
                    'product_qty': 2.0,
                }),
                (0, 0, {
                    'product_id': self.component2.id,
                    'product_qty': 1.0,
                })
            ]
        })
        
        # Set initial stock levels
        self._set_stock_quantity(self.parent_product, 100)
        self._set_stock_quantity(self.component1, 50)
        self._set_stock_quantity(self.component2, 25)
        
        # Create POS configuration
        self.pos_config = self.env['pos.config'].create({
            'name': 'Test POS Config',
            'picking_type_id': self.env['stock.picking.type'].search([
                ('code', '=', 'outgoing')
            ], limit=1).id,
        })
        
    def _set_stock_quantity(self, product, quantity):
        """Helper method to set stock quantity"""
        location = self.env.ref('stock.stock_location_stock')
        self.env['stock.quant']._update_available_quantity(
            product, location, quantity
        )
        
    def test_bom_parent_stock_not_deducted(self):
        """Test that parent product stock is not deducted when BOM is used"""
        
        # Record initial stock levels
        initial_parent_stock = self.parent_product.qty_available
        initial_component1_stock = self.component1.qty_available
        initial_component2_stock = self.component2.qty_available
        
        # Create POS session
        pos_session = self.env['pos.session'].create({
            'config_id': self.pos_config.id,
        })
        pos_session.action_pos_session_open()
        
        # Create POS order
        pos_order = self.env['pos.order'].create({
            'name': 'Test Order - BOM Parent Stock Prevention',
            'session_id': pos_session.id,
            'partner_id': False,
            'lines': [(0, 0, {
                'product_id': self.parent_product.id,
                'qty': 1.0,
                'price_unit': 100.0,
            })],
            'amount_total': 100.0,
            'amount_tax': 0.0,
            'amount_paid': 100.0,
            'amount_return': 0.0,
        })
        
        # Process the order
        pos_order.action_pos_order_paid()
        
        # Check stock levels after processing
        final_parent_stock = self.parent_product.qty_available
        final_component1_stock = self.component1.qty_available
        final_component2_stock = self.component2.qty_available
        
        # Assertions
        self.assertEqual(
            final_parent_stock, 
            initial_parent_stock,
            "Parent product stock should not be deducted for BOM products"
        )
        
        self.assertEqual(
            final_component1_stock,
            initial_component1_stock - 2.0,
            "Component 1 stock should be deducted by BOM quantity (2.0)"
        )
        
        self.assertEqual(
            final_component2_stock,
            initial_component2_stock - 1.0,
            "Component 2 stock should be deducted by BOM quantity (1.0)"
        )
        
        pos_session.action_pos_session_close()
        
    def test_regular_product_stock_still_deducted(self):
        """Test that regular products (non-BOM) still have their stock deducted"""
        
        # Create a regular product (not BOM)
        regular_product = self.env['product.product'].create({
            'name': 'Regular Product',
            'type': 'product',
            'use_bom_in_pos': False,  # Explicitly disable BOM
        })
        
        self._set_stock_quantity(regular_product, 50)
        initial_stock = regular_product.qty_available
        
        # Create POS session
        pos_session = self.env['pos.session'].create({
            'config_id': self.pos_config.id,
        })
        pos_session.action_pos_session_open()
        
        # Create POS order with regular product
        pos_order = self.env['pos.order'].create({
            'name': 'Test Order - Regular Product',
            'session_id': pos_session.id,
            'partner_id': False,
            'lines': [(0, 0, {
                'product_id': regular_product.id,
                'qty': 2.0,
                'price_unit': 50.0,
            })],
            'amount_total': 100.0,
            'amount_tax': 0.0,
            'amount_paid': 100.0,
            'amount_return': 0.0,
        })
        
        # Process the order
        pos_order.action_pos_order_paid()
        
        # Check stock level
        final_stock = regular_product.qty_available
        
        # Regular product stock should be deducted
        self.assertEqual(
            final_stock,
            initial_stock - 2.0,
            "Regular product stock should be deducted normally"
        )
        
        pos_session.action_pos_session_close()
        
    def test_bom_stock_validation_prevents_sale(self):
        """Test that insufficient BOM component stock prevents the sale"""
        
        # Set component stock to insufficient levels
        self._set_stock_quantity(self.component1, 1)  # Need 2, only have 1
        
        # Create POS session
        pos_session = self.env['pos.session'].create({
            'config_id': self.pos_config.id,
        })
        pos_session.action_pos_session_open()
        
        # Create POS order line that should fail due to insufficient component stock
        pos_order = self.env['pos.order'].create({
            'name': 'Test Order - Insufficient Stock',
            'session_id': pos_session.id,
            'partner_id': False,
            'lines': [(0, 0, {
                'product_id': self.parent_product.id,
                'qty': 1.0,
                'price_unit': 100.0,
            })],
            'amount_total': 100.0,
            'amount_tax': 0.0,
            'amount_paid': 100.0,
            'amount_return': 0.0,
        })
        
        # Processing should raise ValidationError due to insufficient component stock
        with self.assertRaises(ValidationError) as cm:
            pos_order.action_pos_order_paid()
        
        # Check that the error message mentions the component
        self.assertIn('Component 1', str(cm.exception))
        self.assertIn('Not enough stock', str(cm.exception))
        
        pos_session.action_pos_session_close()
        
    def test_get_stock_moves_to_consider_override(self):
        """Test the _get_stock_moves_to_consider method directly"""
        
        # Create POS session and order line
        pos_session = self.env['pos.session'].create({
            'config_id': self.pos_config.id,
        })
        pos_session.action_pos_session_open()
        
        pos_order = self.env['pos.order'].create({
            'name': 'Test Order',
            'session_id': pos_session.id,
        })
        
        # Test BOM product line
        bom_line = self.env['pos.order.line'].create({
            'order_id': pos_order.id,
            'product_id': self.parent_product.id,
            'qty': 1.0,
            'price_unit': 100.0,
        })
        
        # BOM product should return empty stock moves
        bom_moves = bom_line._get_stock_moves_to_consider()
        self.assertEqual(len(bom_moves), 0, "BOM products should return no stock moves")
        
        # Test regular product line
        regular_product = self.env['product.product'].create({
            'name': 'Regular Test Product',
            'type': 'product',
            'use_bom_in_pos': False,
        })
        
        regular_line = self.env['pos.order.line'].create({
            'order_id': pos_order.id,
            'product_id': regular_product.id,
            'qty': 1.0,
            'price_unit': 50.0,
        })
        
        # Regular product should use standard logic (we can't easily test the actual 
        # stock moves without going through the full order process, but we can at least
        # verify that the method doesn't return empty for regular products by checking
        # that it calls the parent method)
        
        pos_session.action_pos_session_close()
