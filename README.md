# POS BOM Integration

This Odoo addon integrates Bill of Materials (BOM) functionality with Point of Sale, automatically deducting BOM components from inventory when products with BOM are sold.

## Features

- **BOM Integration**: Seamlessly integrates existing BOM data with POS
- **Automatic Inventory Deduction**: When a product with BOM is sold, the BOM components are automatically deducted from inventory
- **Stock Validation**: Prevents sales when insufficient stock is available for BOM components
- **Visual Indicators**: Shows BOM products in product views and POS interface
- **Flexible Configuration**: Enable/disable BOM usage per product

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

### In POS

1. Open the POS interface
2. Products with BOM enabled will show a "BOM" badge
3. When adding a BOM product to cart:
   - System checks stock availability for all BOM components
   - Prevents sale if insufficient stock
   - Shows warning messages for stock issues

### Backend Management

1. **Product Form**: Shows BOM information and allows toggling BOM usage
2. **POS Orders**: Displays BOM information in order lines
3. **Inventory Moves**: Automatic stock moves are created for BOM components

## Technical Details

### Models Extended

- `product.template`: Added BOM-related fields and methods
- `pos.order`: Added BOM processing logic
- `pos.order.line`: Added BOM inventory move creation

### Key Methods

- `get_bom_components()`: Returns BOM components for a product
- `_create_bom_inventory_moves()`: Creates inventory moves for BOM components
- `_process_bom_inventory_moves()`: Processes all BOM moves in an order

### Stock Moves

When a BOM product is sold:
1. System calculates required quantities for each BOM component
2. Creates stock moves from main location to production location
3. Automatically confirms and processes the moves
4. Updates inventory levels accordingly

### Frontend Integration

- JavaScript extensions for real-time stock validation
- Enhanced product information display
- Improved order processing with BOM data

## Troubleshooting

### Common Issues

1. **"Not enough stock" error**: Check inventory levels for BOM components
2. **BOM not showing**: Ensure BOM is active and product has "Use BOM in POS" enabled
3. **Stock moves not created**: Check user permissions and location settings

### Permissions

Users need access to:
- POS operations
- Stock moves
- BOM reading permissions

## Support

For issues or feature requests, please contact your system administrator or the module developer.

## License

This module is licensed under the same terms as Odoo Community Edition.
