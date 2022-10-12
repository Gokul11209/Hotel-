# See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class HotelHousekeeping(models.Model):
    _name = "hotel.housekeeping"
    _description = "Hotel Housekeeping"
    _rec_name = "room_id"

    current_date = fields.Date(
        "Today's Date",
        required=True,
        index=True,
        states={"done": [("readonly", True)]},
        default=fields.Date.today,
    )
    clean_type = fields.Selection(
        [
            ("daily", "Daily"),
            ("checkin", "Check-In"),
            ("checkout", "Check-Out"),
        ],
        "Clean Type",
        required=True,
        states={"done": [("readonly", True)]},
    )
    room_id = fields.Many2one("hotel.reservation", "Reservation ID")
    activity_line_ids = fields.One2many(
        "hotel.housekeeping.activities",
        "housekeeping_id",
        "Activities",
        states={"done": [("readonly", True)]},
        help="Detail of housekeeping \
                                        activities",
    )
    inspector_id = fields.Many2one(
        "res.users",
        "Inspector",
        required=True,
        states={"done": [("readonly", True)]},
    )
    inspect_date_time = fields.Datetime(
        "Inspect Date Time",
        required=True,
        states={"done": [("readonly", True)]},
    )
    quality = fields.Selection(
        [
            ("excellent", "Excellent"),
            ("good", "Good"),
            ("average", "Average"),
            ("bad", "Bad"),
            ("ok", "Ok"),
        ],
        "Quality",
        states={"done": [("readonly", True)]},
        help="Inspector inspect the room and mark \
                                as Excellent, Average, Bad, Good or Ok. ",
    )
    state = fields.Selection(
        [
            ("inspect", "Inspect"),
            ("dirty", "Dirty"),
            ("clean", "Clean"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        "State",
        states={"done": [("readonly", True)]},
        required=True,
        readonly=True,
        default="inspect",
    )

    housekeeping_cancel_remarks = fields.Text(string='Housekeeping Cancel Remarks')
    housekeeping_cancel_remarks_2 = fields.Text(string='Housekeeping Cancel Remarks')
    housekeeping_cancel_remarks_3 = fields.Text(string='Housekeeping Cancel Remarks')

    def house_keeping_cancel(self):
        view_id = self.env['housekeeping.cancel']
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hotel Management Table Order Cancel Remarks',
            'res_model': 'housekeeping.cancel',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('hotel_housekeeping.hotel_management_table_cancel_remarks_wizard', False).id,
            'target': 'new',
        }

    def action_set_to_dirty(self):
        """
        This method is used to change the state
        to dirty of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "dirty", "quality": False})
        self.activity_line_ids.write({"is_clean": False, "is_dirty": True})

    def room_cancel(self):
        """
        This method is used to change the state
        to cancel of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "cancel", "quality": False})

    def get_service_order_line_items(self):
        line_vals = []
        # for line in self.activity_line_ids:
        if self.activity_line_ids:
            vals = [0, 0, {
                'product_id': 12,
                'product_uom_qty': len(self.activity_line_ids),
                # 'name': line.housekeeper_id.name,

            }]
            line_vals.append(vals)
        return line_vals

    def proforma_housekeeping_activity(self):
        line_vals = []
        # for line in self.activity_line_ids:
        if self.room_id:
            vals = [0, 0, {
                'current_date': self.current_date,
                'clean_type': self.clean_type,
                'room_id': self.room_id.id,
                'inspector_id': self.inspector_id.id,
                'inspect_date_time': self.inspect_date_time,

            }]
            line_vals.append(vals)
        return line_vals



    def room_done(self):
        """
        This method is used to change the state
        to done of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """

        folio_id = self.env['hotel.folio'].sudo().search([('reservation_id', '=', self.room_id.id)])
        folio_id.sudo().write({
            'hotel_house_keeping_orders_ids': self.proforma_housekeeping_activity(),
            'service_line_ids': self.get_service_order_line_items(),
        })
        if not self.quality:
            raise ValidationError(_("Alert!, Please update quality of work!"))

        # else:
        #     raise ValidationError(_("Alert!, Please Create a Folio against the Reservation"))
        self.write({"state": "done"})





    def room_inspect(self):
        """
        This method is used to change the state
        to inspect of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "inspect", "quality": False})

    def room_clean(self):
        """
        This method is used to change the state
        to clean of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "clean", "quality": False})
        self.activity_line_ids.write({"is_clean": True, "is_dirty": False})
