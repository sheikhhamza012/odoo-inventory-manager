#!/usr/bin/env python3
"""
Test script to verify BOM data is being loaded in POS
Run this in Odoo shell to check backend data
"""

def test_backend_bom_data():
    print("=== Testing Backend BOM Data Loading ===")
    
    # Find POS sessions
    pos_sessions = env['pos.session'].search([('state', '=', 'opened')], limit=1)
    if not pos_sessions:
        pos_sessions = env['pos.session'].search([], limit=1)
    
    if not pos_sessions:
        print("❌ No POS sessions found")
        return
    
    session = pos_sessions[0]
    print(f"✓ Using POS session: {session.name} (State: {session.state})")
    
    # Test the _get_pos_ui_product_product method
    print("\n--- Testing _get_pos_ui_product_product method ---")
    
    try:
        # Get the product data as POS would
        params = {}
        products_data = session._get_pos_ui_product_product(params)
        
        print(f"✓ Loaded {len(products_data)} products from POS UI method")
        
        # Find BOM products in the data
        bom_products = [p for p in products_data if p.get('use_bom_in_pos') and p.get('has_bom')]
        print(f"✓ Found {len(bom_products)} BOM products in POS data")
        
        # Show details of BOM products
        for product_data in bom_products[:3]:  # Show first 3
            print(f"  - {product_data.get('name', 'Unknown')}: "
                  f"use_bom_in_pos={product_data.get('use_bom_in_pos')}, "
                  f"has_bom={product_data.get('has_bom')}")
        
        if not bom_products:
            print("⚠️  No BOM products found in POS data")
            
            # Check if we have products with BOM in the database
            print("\n--- Checking database for BOM products ---")
            db_bom_products = env['product.product'].search([
                ('use_bom_in_pos', '=', True),
                ('available_in_pos', '=', True)
            ])
            
            print(f"Found {len(db_bom_products)} BOM products in database:")
            for product in db_bom_products[:3]:
                print(f"  - {product.name}: use_bom_in_pos={product.use_bom_in_pos}, "
                      f"has_bom={product.has_bom}, available_in_pos={product.available_in_pos}")
                      
            if db_bom_products and not bom_products:
                print("❌ BOM products exist in DB but not in POS data - method not working")
        
    except Exception as e:
        print(f"❌ Error calling _get_pos_ui_product_product: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n--- Testing Product Template Methods ---")
    
    # Find a product template with BOM
    bom_templates = env['product.template'].search([
        ('use_bom_in_pos', '=', True),
        ('has_bom', '=', True)
    ], limit=1)
    
    if bom_templates:
        template = bom_templates[0]
        print(f"✓ Testing with template: {template.name}")
        
        # Test get_bom_components
        try:
            components = template.get_bom_components()
            print(f"✓ get_bom_components returned {len(components)} components")
            for comp in components:
                print(f"  - {comp['product_name']}: qty={comp['quantity']}")
        except Exception as e:
            print(f"❌ get_bom_components failed: {e}")
        
        # Test validate_bom_stock
        try:
            validation = template.validate_bom_stock(1)
            print(f"✓ validate_bom_stock result: {validation}")
        except Exception as e:
            print(f"❌ validate_bom_stock failed: {e}")
    else:
        print("❌ No BOM templates found")
    
    print("\n--- Summary ---")
    print("1. Check if BOM products show in POS data")
    print("2. Verify _get_pos_ui_product_product is including BOM fields")
    print("3. Ensure products have available_in_pos=True")
    print("4. Check if POS session is properly loading the method")

if __name__ == "__main__":
    print("Run this in Odoo shell:")
    print("exec(open('addons/pos_bom_integration/test_backend_data.py').read())")
    print("test_backend_bom_data()")
