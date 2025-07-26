{
    'name': 'POS BOM Integration - Advanced Stock Validation',
    'version': '17.0.1.2.0',
    'category': 'Point of Sale',
    'sequence': 10,
    'summary': 'Dual-level BOM validation in POS with real-time stock checking and automatic inventory deduction',
    'description': """
POS BOM Integration - Advanced Stock Validation
==============================================

Comprehensive Bill of Materials (BOM) integration for Odoo Point of Sale with advanced validation features.

Key Features:
* **Dual-Level Validation**: Validates BOM stock both on product click AND order confirmation
* **Real-time Stock Checking**: Immediate validation when products are selected in POS
* **Automatic Inventory Deduction**: BOM components are automatically deducted from inventory
* **Smart Error Handling**: Clear error messages showing which components lack sufficient stock
* **Configurable Validation**: Enable/disable BOM validation per POS configuration
* **Fallback Data Loading**: Automatically fetches BOM data if not initially loaded
* **Debug Support**: Built-in debugging tools and console helpers for troubleshooting

How it Works:
1. When clicking on a BOM product, the system immediately validates component stock
2. If insufficient stock, shows error dialog and prevents adding to cart
3. Before payment, validates all BOM products in the order as final check
4. Only allows order completion when all BOM components have adequate stock
5. Automatically deducts BOM components from inventory upon successful order

Perfect for:
* Manufacturing companies selling finished products through POS
* Restaurants with recipe-based menu items
* Retail stores with bundled products
* Any business needing automatic component stock tracking

Technical Features:
* Odoo 17 compatible with proper ORM service usage
* Enhanced JavaScript with async/await for better performance
* Comprehensive error handling and user feedback
* Multiple validation entry points for maximum reliability
* Extensive debugging tools for easy troubleshooting
    """,
    'author': 'Sheikh Hamza',
    'website': 'https://github.com/sheikhhamza012/pos_bom_integration',
    'license': 'LGPL-3',
    'maintainer': 'Sheikh Hamza',
    'contributors': [
        'Sheikh Hamza <sheikhhamza012@example.com>',
    ],
    'depends': [
        'point_of_sale',
        'mrp',
        'stock',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/pos_order_views.xml',
        'views/pos_config_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_bom_integration/static/src/js/pos_bom_integration.js',
        ],
    },
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
        'static/description/screenshot_1.png',
        'static/description/screenshot_2.png',
        'static/description/screenshot_3.png',
    ],
    'price': 0.00,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'application': False,
    'pre_init_hook': None,
    'post_init_hook': None,
    'uninstall_hook': None,
    'bootstrap': False,
    'cloc_exclude': [
        'debug/**/*',
        'tests/**/*',
    ],
}
