# POS BOM Integration

This Odoo addon integrates Bill of Materials (BOM) functionality with Point of Sale, providing comprehensive BOM validation and automatic inventory deduction when products with BOM are sold.

## Features

- **Dual-Level BOM Validation**: Validates BOM stock both when clicking on products AND when confirming orders
- **Real-time Stock Checking**: Instant validation when products are selected in POS
- **Automatic Inventory Deduction**: When a product with BOM is sold, the BOM components are automatically deducted from inventory
- **Comprehensive Error Handling**: Clear error messages showing which BOM components lack sufficient stock
- **Configurable Validation**: Enable/disable BOM validation per POS configuration
- **Fallback Data Loading**: Automatically fetches BOM data if not initially loaded
- **Visual Indicators**: Shows BOM products in product views and POS interface
- **Debug Support**: Built-in debugging tools and console helpers

## Installation

1. Copy the `pos_bom_integration` folder to your Odoo addons directory
2. Update your addon list in Odoo
3. Install the "POS BOM Integration" module

## Dependencies

- `point_of_sale`: Core POS functionality
- `mrp`: Manufacturing module for BOM management
- `stock`: Inventory management

## Configuration

### Product Setup

1. Go to **Inventory > Products > Products**
2. Open a product that has a BOM
3. Enable **Use BOM in POS** checkbox
4. The product will now automatically deduct BOM components when sold in POS

### BOM Creation

1. Go to **Manufacturing > Products > Bills of Materials**
2. Create a BOM for your product
3. Add the required components with their quantities
4. Save the BOM

## Usage

### Enhanced BOM Validation

This module provides **two levels of validation** to ensure BOM products cannot be sold without sufficient component stock:

#### 1. Product Click Validation (Immediate)
1. Click on any BOM product in POS
2. System immediately validates all BOM component stock
3. If insufficient stock:
   - Shows error dialog with specific component details
   - Product is NOT added to cart
   - Error message shows exactly which component lacks stock
4. If stock is sufficient:
   - Product is added to cart normally

#### 2. Order Confirmation Validation (Final Check)
1. Click "Order" or "Payment" button
2. System validates ALL BOM products in the current order
3. If any BOM product has insufficient component stock:
   - Shows comprehensive error dialog
   - Payment is blocked until stock issues are resolved
4. If all validations pass:
   - Order proceeds normally
   - BOM components are automatically deducted from inventory

### Backend Management

1. **Product Form**: Shows BOM information and allows toggling BOM usage
2. **POS Orders**: Displays BOM information in order lines
3. **Inventory Moves**: Automatic stock moves are created for BOM components

## Technical Details

### Models Extended

- `product.template`: Added BOM-related fields and validation methods
- `pos.order`: Added BOM processing and validation logic
- `pos.order.line`: Added BOM inventory move creation
- `pos.session`: Enhanced product data loading with BOM fields
- `pos.config`: Added BOM validation configuration

### Key Backend Methods

- `get_bom_components()`: Returns BOM components for a product
- `validate_bom_stock()`: Validates BOM component stock availability
- `validate_bom_stock_rpc()`: RPC method for frontend validation calls
- `validate_order_bom_stock()`: Validates all BOM products in an order
- `_create_bom_inventory_moves()`: Creates inventory moves for BOM components
- `_process_bom_inventory_moves()`: Processes all BOM moves in an order
- `create_from_ui()`: Enhanced with BOM validation during order creation

### Frontend Integration

- **Real-time Validation**: JavaScript patches for immediate stock checking
- **Dual Validation Points**: Product click AND order confirmation
- **Fallback Data Loading**: Automatic BOM data fetching if missing
- **Enhanced Error Handling**: Clear, specific error messages
- **Debug Support**: Console helpers and logging for troubleshooting

### Stock Moves

When a BOM product is sold:
1. System calculates required quantities for each BOM component
2. Creates stock moves from main location to production location
3. Automatically confirms and processes the moves
4. Updates inventory levels accordingly

### Frontend Integration

## Configuration

### POS Configuration

1. Go to **Point of Sale > Configuration > Point of Sale**
2. Edit your POS configuration
3. Enable **"Enable BOM Stock Validation"** checkbox
4. This setting controls whether BOM validation is active for this POS

### Disabling Validation (For Testing)

To temporarily disable BOM validation:
1. Set `enable_bom_validation = False` on your POS config
2. Or use the debug console: `bomDebug.refreshProductBomData('product_name')`

## Debugging & Testing

### Console Debug Tools

Open browser console (F12) and paste the contents of `debug/console_helpers.js` to access:
- `bomDebug.checkAllProducts()` - List all BOM products and their status
- `bomDebug.testValidation('product_name')` - Test validation for specific product
- `bomDebug.refreshProductBomData('product_name')` - Refresh BOM data for product
- `bomDebug.testAddProduct('product_name')` - Test adding product to order

### Backend Testing

Run in Odoo shell:
```python
exec(open('addons/pos_bom_integration/debug/test_enhanced_validation.py').read())
test_enhanced_validation()
```

**Note**: All debugging tools and test scripts are located in the `debug/` folder. See `debug/README.md` for complete documentation.

## Troubleshooting

### Common Issues

1. **"Not enough stock" error**: Check inventory levels for BOM components
2. **BOM not showing**: Ensure BOM is active and product has "Use BOM in POS" enabled
3. **Validation not working on product click**: Check browser console for errors, clear cache
4. **BOM fields showing as undefined**: Run `bomDebug.checkAllProducts()` to diagnose
5. **Stock moves not created**: Check user permissions and location settings

### Debug Information

If validation isn't working:
1. Check browser console for error messages
2. Verify product has `use_bom_in_pos = True` and `has_bom = True`
3. Confirm BOM has active components with proper stock
4. Clear browser cache and restart Odoo in development mode
5. Run backend test script to verify data loading

### Permissions

Users need access to:
- POS operations
- Stock moves
- BOM reading permissions
- Product template read access

## Support

For issues or feature requests, please contact your system administrator or the module developer.

## License

This module is licensed under the same terms as Odoo Community Edition.
