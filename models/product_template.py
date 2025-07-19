from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_bom = fields.Boolean(
        string='Has BOM',
        compute='_compute_has_bom',
        store=True,
        help='Indicates if this product has a Bill of Materials'
    )
    
    bom_ids = fields.One2many(
        'mrp.bom', 
        'product_tmpl_id', 
        string='Bills of Materials'
    )
    
    use_bom_in_pos = fields.Boolean(
        string='Use BOM in POS',
        default=False,
        help='When enabled, selling this product in POS will automatically deduct BOM components from inventory'
    )

    @api.depends('bom_ids')
    def _compute_has_bom(self):
        for record in self:
            record.has_bom = bool(record.bom_ids)

    def get_bom_components(self):
        """Get BOM components for this product"""
        self.ensure_one()
        if not self.bom_ids:
            return []
        
        # Get the first active BOM
        bom = self.bom_ids.filtered(lambda b: b.active)[:1]
        if not bom:
            return []
        
        components = []
        for line in bom.bom_line_ids:
            components.append({
                'product_id': line.product_id.id,
                'product_name': line.product_id.name,
                'quantity': line.product_qty,
                'uom_id': line.product_uom_id.id,
                'uom_name': line.product_uom_id.name,
            })
        return components
