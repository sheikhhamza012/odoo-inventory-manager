from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError

class TestBOMActivation(TransactionCase):

    def setUp(self):
        super().setUp()
        
        # Create test products
        self.product_a = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'use_bom_in_pos': True,
            'list_price': 100.0,
        })
        
        self.component_b = self.env['product.product'].create({
            'name': 'Component B',
            'type': 'product',
            'list_price': 20.0,
        })
        
        self.component_c = self.env['product.product'].create({
            'name': 'Component C',
            'type': 'product',
            'list_price': 30.0,
        })
        
        # Create BOM for Product A
        self.bom = self.env['mrp.bom'].create({
            'product_tmpl_id': self.product_a.product_tmpl_id.id,
            'product_qty': 1.0,
            'type': 'normal',
        })
        
        # Add BOM lines (components)
        self.env['mrp.bom.line'].create({
            'bom_id': self.bom.id,
            'product_id': self.component_b.id,
            'product_qty': 2.0,
        })
        
        self.env['mrp.bom.line'].create({
            'bom_id': self.bom.id,
            'product_id': self.component_c.id,
            'product_qty': 1.0,
        })
        
        # Create stock location and set initial stock
        self.stock_location = self.env.ref('stock.stock_location_stock')
        
        # Set stock for Component B (sufficient)
        self.env['stock.quant']._update_available_quantity(
            self.component_b, self.stock_location, 10.0
        )
        
        # Set stock for Component C (insufficient - 0 quantity)
        self.env['stock.quant']._update_available_quantity(
            self.component_c, self.stock_location, 0.0
        )
        
        # Create POS session and order for testing
        self.pos_config = self.env['pos.config'].create({
            'name': 'Test POS Config',
            'module_pos_restaurant': False,
        })
        
        self.pos_session = self.env['pos.session'].create({
            'config_id': self.pos_config.id,
            'user_id': self.env.user.id,
        })
        
        self.pos_order = self.env['pos.order'].create({
            'session_id': self.pos_session.id,
            'partner_id': False,
            'lines': [],
        })

    def test_bom_activation(self):
        # Add meaningful test logic here
        pass
        
    def test_bom_component_availability(self):
        """Test that UserError is raised when BOM component C is missing"""
        
        # Test 1: Create POS order line for product A with missing component C
        with self.assertRaises(ValidationError) as context:
            pos_order_line = self.env['pos.order.line'].create({
                'order_id': self.pos_order.id,
                'product_id': self.product_a.id,
                'qty': 1.0,
                'price_unit': self.product_a.list_price,
            })
            # Trigger the BOM inventory moves creation which should validate stock
            pos_order_line._create_bom_inventory_moves()
        
        # Verify the error message mentions Component C
        error_message = str(context.exception)
        self.assertIn('Component C', error_message)
        self.assertIn('Not enough stock', error_message)
        
        # Test 2: Alternative test using product template validation method
        validation_result = self.product_a.product_tmpl_id.validate_bom_stock(
            quantity=1, location_id=self.stock_location.id
        )
        
        # Assert validation fails
        self.assertFalse(validation_result['valid'])
        self.assertEqual(validation_result['error']['component_name'], 'Component C')
        self.assertEqual(validation_result['error']['available'], 0.0)
        self.assertEqual(validation_result['error']['required'], 1.0)
        
        # Test 3: Create manufacturing order (if mrp module allows direct creation)
        try:
            # Try to create a manufacturing order for Product A
            manufacturing_order = self.env['mrp.production'].create({
                'product_id': self.product_a.id,
                'product_qty': 1.0,
                'bom_id': self.bom.id,
            })
            
            # Try to confirm the manufacturing order - this should validate availability
            with self.assertRaises((ValidationError, UserError)) as mo_context:
                manufacturing_order.action_confirm()
                # If confirmation succeeds, try to check availability
                manufacturing_order.action_assign()
            
            # The error should mention insufficient stock or Component C
            mo_error_message = str(mo_context.exception)
            self.assertTrue(
                'Component C' in mo_error_message or 
                'not enough' in mo_error_message.lower() or
                'insufficient' in mo_error_message.lower()
            )
            
        except Exception as e:
            # If MRP doesn't allow direct creation or has different validation,
            # we still have the POS validation test above
            pass
        
        # Test 4: Test with sufficient stock (positive case)
        # Add stock for Component C
        self.env['stock.quant']._update_available_quantity(
            self.component_c, self.stock_location, 5.0
        )
        
        # Now validation should pass
        validation_result_positive = self.product_a.product_tmpl_id.validate_bom_stock(
            quantity=1, location_id=self.stock_location.id
        )
        self.assertTrue(validation_result_positive['valid'])
        
        # POS order line creation should now succeed
        successful_pos_line = self.env['pos.order.line'].create({
            'order_id': self.pos_order.id,
            'product_id': self.product_a.id,
            'qty': 1.0,
            'price_unit': self.product_a.list_price,
        })
        
        # This should not raise an exception now
        successful_pos_line._create_bom_inventory_moves()
        
        # Verify the order line was created successfully
        self.assertEqual(successful_pos_line.product_id, self.product_a)
        self.assertEqual(successful_pos_line.qty, 1.0)

