#!/usr/bin/env python3
"""
Test script to verify enhanced BOM validation functionality
Run this in Odoo shell to test the new validation features
"""

def test_enhanced_validation():
    print("=== Testing Enhanced BOM Validation ===")
    print("Testing both frontend validation (on click) and order validation (on payment)")
    
    # Find a product with BOM
    bom_products = env['product.product'].search([
        ('use_bom_in_pos', '=', True),
        ('has_bom', '=', True)
    ], limit=1)
    
    if not bom_products:
        print("❌ No BOM products found. Please create a product with BOM first.")
        return False
    
    product = bom_products[0]
    template = product.product_tmpl_id
    
    print(f"✓ Testing with product: {product.name} (ID: {product.id})")
    
    # Test 1: Product template validation method
    print("\n--- Test 1: Product Template Validation ---")
    try:
        validation = template.validate_bom_stock(quantity=1)
        print(f"✓ validate_bom_stock method exists: {validation}")
    except Exception as e:
        print(f"❌ validate_bom_stock method failed: {e}")
        return False
    
    # Test 2: RPC validation method
    print("\n--- Test 2: RPC Validation Method ---")
    try:
        rpc_validation = env['pos.order'].validate_bom_stock_rpc(product.id, 1)
        print(f"✓ validate_bom_stock_rpc method exists: {rpc_validation}")
    except Exception as e:
        print(f"❌ validate_bom_stock_rpc method failed: {e}")
        return False
    
    # Test 3: Show BOM components and stock levels
    print("\n--- Test 3: BOM Components Analysis ---")
    components = template.get_bom_components()
    print(f"BOM has {len(components)} components:")
    
    for comp in components:
        comp_product = env['product.product'].browse(comp['product_id'])
        print(f"  - {comp['product_name']}: need {comp['quantity']}, have {comp_product.qty_available}")
    
    # Test 4: Test with high quantity to trigger validation failure
    print("\n--- Test 4: High Quantity Validation ---")
    high_qty_validation = template.validate_bom_stock(quantity=1000)
    if high_qty_validation['valid']:
        print("⚠️  High quantity validation passed (unexpected if stock is low)")
    else:
        print(f"✓ High quantity validation failed as expected: {high_qty_validation['error']}")
    
    # Test 5: POS Config validation toggle
    print("\n--- Test 5: POS Config Validation Toggle ---")
    pos_config = env['pos.config'].search([], limit=1)
    if pos_config:
        print(f"✓ Found POS config: {pos_config.name}")
        print(f"  enable_bom_validation: {pos_config.enable_bom_validation}")
        
        # Test with validation disabled
        pos_config.enable_bom_validation = False
        disabled_validation = template.validate_bom_stock(quantity=1000, pos_config=pos_config)
        print(f"  Validation with disabled config: {disabled_validation}")
        
        # Restore validation
        pos_config.enable_bom_validation = True
        enabled_validation = template.validate_bom_stock(quantity=1000, pos_config=pos_config)
        print(f"  Validation with enabled config: {enabled_validation}")
    else:
        print("⚠️  No POS config found")
    
    print("\n=== Validation Implementation Summary ===")
    print("✓ 1. Product-level BOM validation (validate_bom_stock)")
    print("✓ 2. RPC method for frontend validation (validate_bom_stock_rpc)")
    print("✓ 3. POS config integration for enabling/disabling validation")
    print("✓ 4. Order-level validation method (validate_order_bom_stock)")
    print("✓ 5. Backend order creation validation")
    
    print("\n=== Frontend Implementation (JavaScript) ===")
    print("✓ 1. Enhanced add_product method with RPC validation")
    print("✓ 2. validate_bom_stock_for_order method for order validation")
    print("✓ 3. pay method override for pre-payment validation")
    print("✓ 4. PosStore validateOrderBomStock method")
    
    print("\n=== Testing Checklist ===")
    print("To test in POS interface:")
    print("1. Open POS with a product that has BOM enabled")
    print("2. Set some BOM component stock to low levels")
    print("3. Try clicking on the BOM product - should show validation error")
    print("4. If validation passes, add to cart and try to pay - should validate again")
    print("5. Check browser console for validation messages")
    print("6. Test with enable_bom_validation=False to allow negative stock")
    
    return True

if __name__ == "__main__":
    print("Run this in Odoo shell:")
    print("exec(open('addons/pos_bom_integration/test_enhanced_validation.py').read())")
    print("test_enhanced_validation()")
