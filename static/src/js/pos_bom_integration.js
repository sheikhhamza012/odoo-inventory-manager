/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";
import { Orderline } from "@point_of_sale/app/store/models";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

// Patch PosStore to load BOM data
patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        
        // Process BOM data for products
        if (loadedData['product.product']) {
            for (const product of loadedData['product.product']) {
                if (product.use_bom_in_pos && product.has_bom) {
                    // Load BOM components for this product
                    const bomComponents = await this.env.services.rpc({
                        model: 'product.template',
                        method: 'get_bom_components',
                        args: [product.product_tmpl_id[0]],
                    });
                    product.bom_components = bomComponents;
                }
            }
        }
    },
});

// Patch Order to handle BOM validation
patch(Order.prototype, {
    add_product(product, options) {
        // Check BOM stock availability before adding product
        if (product.use_bom_in_pos && product.has_bom && product.bom_components) {
            const qty = (options && options.quantity) || 1;
            
            for (const component of product.bom_components) {
                const componentProduct = this.pos.db.get_product_by_id(component.product_id);
                if (componentProduct) {
                    const requiredQty = component.quantity * qty;
                    const availableQty = componentProduct.qty_available;
                    
                    if (availableQty < requiredQty) {
                        this.env.services.dialog.add(AlertDialog, {
                            title: this.env._t('Insufficient Stock'),
                            body: this.env._t(
                                `Not enough stock for BOM component "${component.product_name}". ` +
                                `Available: ${availableQty}, Required: ${requiredQty}`
                            ),
                        });
                        return false;
                    }
                }
            }
        }
        
        return super.add_product(product, options);
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
