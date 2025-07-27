#!/usr/bin/env python3
"""
Script to upgrade the pos_bom_integration module
Run this in Odoo shell to add the new field to the database
"""

def upgrade_pos_bom_integration():
    """Upgrade the pos_bom_integration module to add new fields"""
    
    print("=== Upgrading POS BOM Integration Module ===")
    
    # Find the module
    module = env['ir.module.module'].search([('name', '=', 'pos_bom_integration')])
    
    if not module:
        print("❌ Module 'pos_bom_integration' not found")
        return False
    
    print(f"✓ Found module: {module.name} (State: {module.state})")
    
    if module.state == 'installed':
        print("📦 Upgrading module...")
        module.button_upgrade()
        print("✅ Module upgrade initiated")
        
        # Check if field exists after upgrade
        try:
            pos_config = env['pos.config'].search([], limit=1)
            if pos_config:
                # Test if field exists
                field_exists = hasattr(pos_config, 'enable_bom_validation')
                print(f"🔍 Field 'enable_bom_validation' exists: {field_exists}")
                
                if field_exists:
                    print(f"📋 Current value: {pos_config.enable_bom_validation}")
                    print("✅ Field successfully added to database")
                else:
                    print("❌ Field still not accessible after upgrade")
            
        except Exception as e:
            print(f"⚠️  Error checking field: {e}")
            
    elif module.state == 'to upgrade':
        print("⏳ Module is already marked for upgrade. Please restart Odoo server.")
        
    else:
        print(f"⚠️  Module state is '{module.state}'. Install the module first.")
    
    print("\n=== Next Steps ===")
    print("1. If module was upgraded, restart your Odoo server")
    print("2. Refresh your browser (Ctrl+Shift+R)")
    print("3. Go to POS Configuration to see the new field")
    print("4. Test the BOM validation toggle functionality")
    
    return True

if __name__ == "__main__":
    print("Run this in Odoo shell:")
    print("exec(open('addons/pos_bom_integration/upgrade_module.py').read())")
    print("upgrade_pos_bom_integration()")
