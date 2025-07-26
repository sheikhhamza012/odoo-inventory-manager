/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";
import { Orderline } from "@point_of_sale/app/store/models";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

// Comprehensive PosStore patch for BOM data loading and validation
patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        
        // Process BOM data for products - ensure data is available
        if (loadedData['product.product']) {
            console.log('Processing BOM data for', loadedData['product.product'].length, 'products');
            
            for (const product of loadedData['product.product']) {
                // Log the product data to debug
                console.log('Product:', product.display_name || product.name, 
                           'use_bom_in_pos:', product.use_bom_in_pos, 
                           'has_bom:', product.has_bom);
                
                if (product.use_bom_in_pos && product.has_bom) {
                    console.log('Loading BOM components for:', product.display_name || product.name);
                    try {
                        // Load BOM components for this product
                        const bomComponents = await this.env.services.orm.call(
                            'product.template',
                            'get_bom_components',
                            [product.product_tmpl_id[0]]
                        );
                        product.bom_components = bomComponents;
                        console.log('Loaded', bomComponents.length, 'BOM components for', product.display_name);
                    } catch (error) {
                        console.error('Failed to load BOM components for', product.display_name, error);
                    }
                }
            }
        }
    },
    
    async validateOrderBomStock(order) {
        // Validate BOM stock before order processing
        if (!order) {
            order = this.get_order();
        }
        
        if (!order) {
            return { valid: true };
        }
        
        const bomErrors = await order.validate_bom_stock_for_order();
        
        if (bomErrors.length > 0) {
            const errorMessages = bomErrors.map(error => 
                `${error.product_name} (Qty: ${error.quantity}): ${error.error}`
            ).join('\\n');
            
            return {
                valid: false,
                error: `BOM Stock Validation Failed:\\n${errorMessages}`
            };
        }
        
        return { valid: true };
    },
    
    async addProductToCurrentOrder(product, options = {}) {
        // Validate BOM stock before adding product to cart (product card click)
        if (product.use_bom_in_pos && product.has_bom) {
            console.log('ProductCard click - validating BOM product:', product.display_name);
            
            const qty = options.quantity || 1;
            
            try {
                const validation = await this.env.services.orm.call(
                    'pos.order',
                    'validate_bom_stock_rpc',
                    [product.id, qty, this.config.id]
                );
                
                if (!validation.valid) {
                    this.env.services.dialog.add(AlertDialog, {
                        title: 'Insufficient Stock',
                        body: validation.error,
                    });
                    return false; // Don't add to cart
                }
            } catch (error) {
                console.error('BOM validation error on product click:', error);
                this.env.services.dialog.add(AlertDialog, {
                    title: 'Validation Error',
                    body: 'Failed to validate BOM stock. Please try again.',
                });
                return false; // Don't add to cart
            }
        }
        
        // If validation passed or not a BOM product, proceed with normal add
        return super.addProductToCurrentOrder(product, options);
    },
});

// Patch Order to handle BOM validation
patch(Order.prototype, {
    async add_product(product, options) {
        console.log('Order.add_product called for:', product.display_name || product.name, 'BOM enabled:', product.use_bom_in_pos, 'Has BOM:', product.has_bom);
        
        // If BOM fields are undefined, try to fetch them from backend
        if (product.use_bom_in_pos === undefined || product.has_bom === undefined) {
            console.log('BOM fields undefined, fetching from backend for product:', product.display_name);
            try {
                const bomData = await this.env.services.orm.call(
                    'product.product',
                    'read',
                    [[product.id], ['use_bom_in_pos', 'has_bom']]
                );
                
                if (bomData && bomData.length > 0) {
                    product.use_bom_in_pos = bomData[0].use_bom_in_pos;
                    product.has_bom = bomData[0].has_bom;
                    console.log('Updated product BOM fields:', product.use_bom_in_pos, product.has_bom);
                }
            } catch (error) {
                console.error('Failed to fetch BOM data for product:', error);
                // Continue without BOM validation if we can't fetch the data
                return super.add_product(product, options);
            }
        }
        
        // Enhanced BOM stock validation before adding product
        if (product.use_bom_in_pos && product.has_bom) {
            console.log('Validating BOM product in add_product:', product.display_name);
            const qty = (options && options.quantity) || 1;
            
            // Use RPC for real-time validation
            try {
                const validation = await this.env.services.orm.call(
                    'pos.order',
                    'validate_bom_stock_rpc',
                    [product.id, qty, this.pos.config.id]
                );
                
                if (!validation.valid) {
                    this.env.services.dialog.add(AlertDialog, {
                        title: 'Insufficient Stock',
                        body: validation.error,
                    });
                    return false;
                }
            } catch (error) {
                console.error('BOM validation error:', error);
                this.env.services.dialog.add(AlertDialog, {
                    title: 'Validation Error',
                    body: 'Failed to validate BOM stock. Please try again.',
                });
                return false;
            }
        }
        
        return super.add_product(product, options);
    },
    
    async validate_bom_stock_for_order() {
        // Validate BOM stock for all order lines
        const bomErrors = [];
        
        for (const line of this.orderlines) {
            const product = line.product;
            if (product.use_bom_in_pos && product.has_bom) {
                try {
                    const validation = await this.env.services.orm.call(
                        'pos.order',
                        'validate_bom_stock_rpc',
                        [product.id, line.quantity, this.pos.config.id]
                    );
                    
                    if (!validation.valid) {
                        bomErrors.push({
                            product_name: product.display_name,
                            quantity: line.quantity,
                            error: validation.error
                        });
                    }
                } catch (error) {
                    console.error('BOM validation error for product:', product.display_name, error);
                    bomErrors.push({
                        product_name: product.display_name,
                        quantity: line.quantity,
                        error: 'Failed to validate BOM stock'
                    });
                }
            }
        }
        
        return bomErrors;
    },
    
    async pay() {
        // Override pay method to validate BOM stock before payment
        // Validate BOM stock before proceeding with payment
        const bomValidation = await this.pos.validateOrderBomStock(this);
        
        if (!bomValidation.valid) {
            this.env.services.dialog.add(AlertDialog, {
                title: 'Order Validation Failed',
                body: bomValidation.error,
            });
            return false;
        }
        
        return super.pay(...arguments);
    },
    
    export_for_printing() {
        const result = super.export_for_printing();
        
        // Add BOM information to receipt
        if (result.orderlines) {
            for (const line of result.orderlines) {
                const product = this.pos.db.get_product_by_id(line.product_id);
                if (product && product.use_bom_in_pos && product.has_bom) {
                    line.has_bom = true;
                    line.bom_components = product.bom_components || [];
                }
            }
        }
        
        return result;
    },
});

// Patch Orderline to show BOM information
patch(Orderline.prototype, {
    get_bom_info() {
        if (this.product.use_bom_in_pos && this.product.has_bom) {
            return {
                has_bom: true,
                components: this.product.bom_components || [],
                total_components: this.product.bom_components ? this.product.bom_components.length : 0,
            };
        }
        return { has_bom: false };
    },
    
    export_as_JSON() {
        const json = super.export_as_JSON();
        
        // Add BOM information to order line
        if (this.product.use_bom_in_pos && this.product.has_bom) {
            json.has_bom = true;
            json.bom_components = this.product.bom_components || [];
        }
        
        return json;
    },
});
