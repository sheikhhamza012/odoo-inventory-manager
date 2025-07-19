{
    'name': 'POS BOM Integration',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Integrate BOM with POS to automatically deduct inventory components',
    'description': """
        This module integrates Bill of Materials (BOM) functionality with Point of Sale.
        When a product with BOM is sold through POS, it automatically deducts the
        BOM components from inventory based on the BOM quantities.
    """,
    'author': 'Your Company',
    'depends': [
        'point_of_sale',
        'mrp',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/pos_order_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_bom_integration/static/src/js/pos_bom_integration.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
