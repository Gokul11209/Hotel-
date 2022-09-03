from odoo import api, fields, models


class HotelFolio(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ],
        "State",
        readonly=True,
        default="draft")


class AddProofType(models.Model):
    _inherit = 'res.partner'
    _description = 'Guest Proof Register'

    proof_type = fields.Many2one("identity.register", string="Proof Type")
    proof_img=fields.Binary(string="Proof")

