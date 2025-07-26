// Console helper functions for debugging BOM integration
// Copy and paste into browser console when POS is loaded

window.bomDebug = {
    // Check BOM data for all products
    checkAllProducts: function() {
        console.log("=== Checking BOM Data for All Products ===");
        
        if (!odoo.env || !odoo.env.services.pos) {
            console.error("POS not loaded");
            return;
        }
        
        const pos = odoo.env.services.pos;
        const products = Object.values(pos.db.product_by_id || {});
        
        console.log(`Total products: ${products.length}`);
        
        const bomProducts = products.filter(p => p.use_bom_in_pos && p.has_bom);
        const undefinedBomProducts = products.filter(p => 
            p.use_bom_in_pos === undefined || p.has_bom === undefined
        );
        
        console.log(`BOM products (properly loaded): ${bomProducts.length}`);
        console.log(`Products with undefined BOM fields: ${undefinedBomProducts.length}`);
        
        if (bomProducts.length > 0) {
            console.log("BOM Products found:");
            bomProducts.forEach(p => console.log(`  - ${p.display_name}: BOM=${p.has_bom}, Enabled=${p.use_bom_in_pos}`));
        }
        
        if (undefinedBomProducts.length > 0) {
            console.log("Products with undefined BOM fields (first 10):");
            undefinedBomProducts.slice(0, 10).forEach(p => 
                console.log(`  - ${p.display_name}: BOM=${p.has_bom}, Enabled=${p.use_bom_in_pos}`)
            );
        }
        
        return {
            total: products.length,
            bomProducts: bomProducts.length,
            undefinedBom: undefinedBomProducts.length
        };
    },
    
    // Test BOM validation for a specific product
    testValidation: async function(productName) {
        console.log(`=== Testing BOM Validation for "${productName}" ===`);
        
        const pos = odoo.env.services.pos;
        const products = Object.values(pos.db.product_by_id || {});
        const product = products.find(p => (p.display_name || p.name).toLowerCase().includes(productName.toLowerCase()));
        
        if (!product) {
            console.error(`Product "${productName}" not found`);
            return;
        }
        
        console.log("Product found:", product.display_name);
        console.log("BOM enabled:", product.use_bom_in_pos);
        console.log("Has BOM:", product.has_bom);
        
        if (product.use_bom_in_pos && product.has_bom) {
            try {
                const validation = await odoo.env.services.orm.call(
                    'pos.order',
                    'validate_bom_stock_rpc',
                    [product.id, 1, pos.config.id]
                );
                
                console.log("Validation result:", validation);
                return validation;
            } catch (error) {
                console.error("Validation failed:", error);
                return { error: error.message };
            }
        } else {
            console.log("Product is not a BOM product or not enabled");
            return { valid: true, reason: "Not a BOM product" };
        }
    },
    
    // Manually refresh BOM data for a product
    refreshProductBomData: async function(productName) {
        console.log(`=== Refreshing BOM Data for "${productName}" ===`);
        
        const pos = odoo.env.services.pos;
        const products = Object.values(pos.db.product_by_id || {});
        const product = products.find(p => (p.display_name || p.name).toLowerCase().includes(productName.toLowerCase()));
        
        if (!product) {
            console.error(`Product "${productName}" not found`);
            return;
        }
        
        try {
            const bomData = await odoo.env.services.orm.call(
                'product.product',
                'read',
                [[product.id], ['use_bom_in_pos', 'has_bom']]
            );
            
            if (bomData && bomData.length > 0) {
                console.log("Old values:", { use_bom_in_pos: product.use_bom_in_pos, has_bom: product.has_bom });
                product.use_bom_in_pos = bomData[0].use_bom_in_pos;
                product.has_bom = bomData[0].has_bom;
                console.log("New values:", { use_bom_in_pos: product.use_bom_in_pos, has_bom: product.has_bom });
                
                // If it's a BOM product, load components
                if (product.use_bom_in_pos && product.has_bom) {
                    const components = await odoo.env.services.orm.call(
                        'product.template',
                        'get_bom_components',
                        [product.product_tmpl_id[0]]
                    );
                    product.bom_components = components;
                    console.log("Loaded BOM components:", components);
                }
                
                return product;
            }
        } catch (error) {
            console.error("Failed to refresh BOM data:", error);
            return null;    
        }
    },
    
    // Test adding a product to the order
    testAddProduct: async function(productName) {
        console.log(`=== Testing Add Product "${productName}" ===`);
        
        const pos = odoo.env.services.pos;
        const products = Object.values(pos.db.product_by_id || {});
        const product = products.find(p => (p.display_name || p.name).toLowerCase().includes(productName.toLowerCase()));
        
        if (!product) {
            console.error(`Product "${productName}" not found`);
            return;
        }
        
        const order = pos.get_order();
        if (!order) {
            console.error("No current order");
            return;
        }
        
        console.log("Attempting to add product:", product.display_name);
        
        try {
            const result = await order.add_product(product);
            console.log("Add product result:", result);
            return result;
        } catch (error) {
            console.error("Add product failed:", error);
            return null;
        }
    }
};

console.log("BOM Debug helpers loaded. Available methods:");
console.log("- bomDebug.checkAllProducts()");
console.log("- bomDebug.testValidation('product_name')");
console.log("- bomDebug.refreshProductBomData('product_name')");
console.log("- bomDebug.testAddProduct('product_name')");
