# See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta



class QuickRoomReservation(models.TransientModel):
    _name = "quick.room.reservation"
    _description = "Quick Room Reservation"

    partner_id = fields.Many2one(
        "res.partner",
        string="Guest"
    )
    check_in = fields.Datetime("Check In")
    check_out = fields.Datetime("Check Out")
    room_id = fields.Many2one(
        "hotel.room",
        string="Room"
    )
    company_id = fields.Many2one(
        "res.company",
        string="Hotel",
        default=lambda self: self.env.company
    )
    guest_type = fields.Selection(
        [("person", "Individual"),
         ("company", "Company")],
        string="Guest Type",
        default='person'
    )
    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist"
    )
    partner_invoice_id = fields.Many2one(
        "res.partner",
        string="Invoice Address"
    )
    partner_order_id = fields.Many2one(
        "res.partner",
        string="Ordering Contact"
    )
    partner_shipping_id = fields.Many2one(
        "res.partner",
        string="Delivery Address"
    )
    room_image = fields.Binary(
        string='Room Image',
        related='room_id.image_1920'
    )
    adults = fields.Integer("Adults")
    guest_creation = fields.Selection(
        [("exist", "Exist"),
         ("new", "New")],
        string="Guest Status",
        default='new'
    )
    room_amenities_ids = fields.Many2many(
        "hotel.room.amenities",
        string="Room Amenities",
        help="List of room amenities.",
        related='room_id.room_amenities_ids'
    )
    name = fields.Char(string='Guest Name')
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string='E-mail')
    valid_proof = fields.Many2one(
        "identity.register",
        string="Proof Type"
    )
    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High')],
        string='Priority')
    create_guest = fields.Boolean(
        string='Do You Want to Generate a New Guest...?'
    )

    search_mobile = fields.Char('Mobile', readonly=False, store=True)
    choose_payment_mode = fields.Many2one("payment.mode", string="Payment Mode")
    payment_mode_img = fields.Binary(string='Payment Image', related='choose_payment_mode.payment_mode_img')
    journal = fields.Many2one("account.journal", string="Journal")
    advance_amt = fields.Float(string="Advance Payment")
    add_proof_type = fields.Many2one("identity.register", string="Proof Type")
    add_proof = fields.Binary(string='Proof')

    active = fields.Boolean('Active', tracking=True)
    reserve_date = fields.Date(string="Date")
    check_in_time = fields.Char(string="Check In Time")
    check_out_time = fields.Char(string="Check Out Time")


    @api.onchange('search_mobile')
    def _compute_mobile(self):
        if self.search_mobile:
            mobile = self.env['res.partner'].sudo().search([
                ('mobile', '=', self.search_mobile)])
            self.write({
                'partner_id': mobile.id
            })
        else:
            self.write({
                'partner_id': False
            })

    @api.onchange("check_out", "check_in")
    def _on_change_check_out(self):
        """
        When you change checkout or checkin it will check whether
        Checkout date should be greater than Checkin date
        and update dummy field
        -----------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        if (self.check_out and self.check_in) and (self.check_out < self.check_in):
            raise ValidationError(
                _("Checkout date should be greater than Checkin date.")
            )

    @api.onchange("partner_id")
    def _onchange_partner_id_res(self):
        """
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the hotel reservation as well
        ---------------------------------------------------------------------
        @param self: object pointer
        """
        if not self.partner_id:
            self.update(
                {
                    "partner_invoice_id": False,
                    "partner_shipping_id": False,
                    "partner_order_id": False,
                }
            )
        else:
            addr = self.partner_id.address_get(["delivery", "invoice", "contact"])
            self.update(
                {
                    "partner_invoice_id": addr["invoice"],
                    "partner_shipping_id": addr["delivery"],
                    "partner_order_id": addr["contact"],
                    "pricelist_id": self.partner_id.property_product_pricelist.id,
                }
            )

    @api.onchange('search_mobile')
    def onchange_proof(self):
        if self.search_mobile:
            details = self.env['res.partner'].sudo().search([
                ('mobile', '=', self.search_mobile)])
            self.write({
                "add_proof_type": details.proof_type.id
            })

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        res = super(QuickRoomReservation, self).default_get(fields)
        keys = self._context.keys()
        print("===============================", keys,"==================",self._context.values())
        if "date" in keys:
            res.update({"reserve_date": self._context["date"]})
        if "entry" in keys:
            res.update({"check_in_time":self._context["entry"]})
        if "room_id" in keys:
            roomid = self._context["room_id"]
            res.update({"room_id": int(roomid)})
        return res

    def room_reserve(self):

        """
        This method create a new record for hotel.reservation
        -----------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel reservation.
        """
        hotel_advance_pay = self.env["account.payment"]
        hotel_res_obj = self.env["hotel.reservation"]
        for i in self:
            rec = hotel_advance_pay.create(
                {
                    "partner_id": i.partner_id.id,
                    "amount": i.advance_amt,
                    "journal_id": i.journal.id,
                }
            )
        res_partner = self.env['res.partner'].sudo().search([
            ('name', '=', self.partner_id.name)])
        print("=====================", res_partner)
        res_partner.write({
            'proof_img': self.add_proof,
        })
        if self.check_in and self.check_out:
            for res in self:
                if self.advance_amt == 0:
                    print('*************ZERO******************')
                    rec = hotel_res_obj.create(
                        {
                            "partner_id": res.partner_id.id,
                            "partner_invoice_id": res.partner_invoice_id.id,
                            "partner_order_id": res.partner_order_id.id,
                            "partner_shipping_id": res.partner_shipping_id.id,
                            "checkin": res.check_in,
                            "checkout": res.check_out,
                            "company_id": res.company_id.id,
                            "pricelist_id": res.pricelist_id.id,
                            "adults": res.adults,
                            "proof_type":res.add_proof,
                            "advance_payment": res.advance_amt,
                            "reservation_line": [
                                (
                                    0,
                                    0,
                                    {
                                        "reserve": [(6, 0, res.room_id.ids)],
                                        "name": res.room_id.name or " ",
                                    },
                                )
                            ],
                        }
                    )
                else:
                    print('************* NON ZERO******************')
                    hotel_res_obj.create({
                        "partner_id": res.partner_id.id,
                        "partner_invoice_id": res.partner_invoice_id.id,
                        "partner_order_id": res.partner_order_id.id,
                        "partner_shipping_id": res.partner_shipping_id.id,
                        "checkin": res.check_in,
                        "checkout": res.check_out,
                        "company_id": res.company_id.id,
                        "pricelist_id": res.pricelist_id.id,
                        "adults": res.adults,
                        "proof_type": res.add_proof,
                        "state":"confirm",
                        "advance_payment": res.advance_amt,
                        "reservation_line": [
                            (
                                0,
                                0,
                                {
                                    "reserve": [(6, 0, res.room_id.ids)],
                                    "name": res.room_id.name or " ",
                                },
                            )
                        ],
                    })
                    hotel_res_obj_new= self.env["hotel.reservation"].search([
                        ("partner_id", "=", res.partner_id.id),
                        ("checkin", "=", res.check_in),
                        ("checkout", "=", res.check_out),
                        ("adults", "=", res.adults),
                        # ("reservation_line.name", "=", res.room_id.name),
                    ])
                    vals = {
                        "room_id": res.room_id.id,
                        "check_in": res.check_in,
                        "check_out": res.check_out,
                        "state": "assigned",
                        "status": "confirm",
                        "reservation_id": hotel_res_obj_new.id,
                    }
                    # self.env["hotel.room.reservation.line"].create(vals)
                    self.room_id.room_reservation_line_ids.create(vals)

        if self.reserve_date and self.check_in_time and self.check_out_time:
            ref_date1 = self.reserve_date
            chk_in_time = self.check_in_time
            chk_out_time = self.check_out_time
            import datetime
            d11 = str(ref_date1)
            print("================ Zero =====================", self.reserve_date)
            dt21 = datetime.datetime.strptime(d11, '%Y-%m-%d')
            date1 = dt21.strftime("%Y-%m-%d")
            print("The date format is", date1, type(date1))
            d22 = str(chk_in_time)
            dt22 = datetime.datetime.strptime(d22, "%H:%M")
            check_in_time = dt22.strftime("%H:%M")
            datetime_object = date1 + ' ' + check_in_time + ":00"
            print("THe final result is", datetime_object)

            if self.check_out_time:
                d33 = str(chk_out_time)
                dt33 = datetime.datetime.strptime(d33, "%H:%M")
                check_out_time = dt33.strftime("%H:%M")
                datetime_object_2 = date1 + ' ' + check_out_time + ":00"
                print("THe final result is", datetime_object_2)

            for res in self:
                if self.advance_amt == 0:
                    print('*************ZERO******************')
                    rec = hotel_res_obj.create(
                        {
                            "partner_id": res.partner_id.id,
                            "partner_invoice_id": res.partner_invoice_id.id,
                            "partner_order_id": res.partner_order_id.id,
                            "partner_shipping_id": res.partner_shipping_id.id,
                            "checkin": datetime_object,
                            "checkout": datetime_object_2,
                            "company_id": res.company_id.id,
                            "pricelist_id": res.pricelist_id.id,
                            "adults": res.adults,
                            "proof_type": res.add_proof,
                            "advance_payment": res.advance_amt,
                            "reservation_line": [
                                (
                                    0,
                                    0,
                                    {
                                        "reserve": [(6, 0, res.room_id.ids)],
                                        "name": res.room_id.name or " ",
                                    },
                                )
                            ],
                        }
                    )
                else:
                    hotel_res_obj.create({
                        "partner_id": res.partner_id.id,
                        "partner_invoice_id": res.partner_invoice_id.id,
                        "partner_order_id": res.partner_order_id.id,
                        "partner_shipping_id": res.partner_shipping_id.id,
                        "checkin": datetime_object,
                        "checkout": datetime_object_2,
                        "company_id": res.company_id.id,
                        "pricelist_id": res.pricelist_id.id,
                        "adults": res.adults,
                        "proof_type": res.add_proof,
                        "state": "confirm",
                        "advance_payment": res.advance_amt,
                        "reservation_line": [
                            (
                                0,
                                0,
                                {
                                    "reserve": [(6, 0, res.room_id.ids)],
                                    "name": res.room_id.name or " ",
                                },
                            )
                        ],
                    })
                    hotel_res_obj_new = self.env["hotel.reservation"].search([
                        ("partner_id", "=", res.partner_id.id),
                        ("checkin", "=", datetime_object),
                        ("checkout", "=", datetime_object_2),
                        ("adults", "=", res.adults),
                        # ("reservation_line.name", "=", res.room_id.name),
                    ])
                    vals = {
                        "room_id": res.room_id.id,
                        "check_in": datetime_object,
                        "check_out": datetime_object_2,
                        "state": "assigned",
                        "status": "confirm",
                        "reservation_id": hotel_res_obj_new.id,
                    }
                    self.room_id.room_reservation_line_ids.sudo().create(vals)



        return rec

    @api.onchange('create_guest')
    def create_new_guest(self):
        for val in self:
            if val.name and val.create_guest:
                values = {
                    'name': val.name,
                    'email': val.email,
                    'mobile': val.mobile,
                    'company_type': val.guest_type,
                    'proof_type': val.valid_proof.id,
                }
                self.env['res.partner'].sudo().create(values)
                partner = self.env['res.partner'].sudo().search([
                    ('name', '=', self.name)])
                self.write({
                    'guest_creation': 'exist',
                    'partner_id': partner.id,
                })
