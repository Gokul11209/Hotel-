from odoo import api, fields, models, _


class HousekeepingChecklistLine(models.Model):
    _name = 'housekeeping.checklist.line'
    _description = 'House Keeping Checklist Line'

    name = fields.Char(string='Name')
    room_id = fields.Many2one('hotel.folio', string='Company')
    true = fields.Boolean('True')
    false = fields.Boolean('False')
    remarks = fields.Char(string='Remarks')


class RoomChecklistLine(models.Model):
    _name = 'room.checklist.line'
    _description = 'Room Checklist Line'

    name = fields.Char(string='Name')
    room_no = fields.Many2one('hotel.room', string='Company')
    true = fields.Boolean('True')
    false = fields.Boolean('False')
    remarks = fields.Char(string='Remarks')


class HousekepingChecklist(models.Model):
    _inherit = 'hotel.folio'
    _description = 'House Folio '

    ref_no = fields.Many2one("hotel.reservation", "Reservation ID")
    ref_name = fields.Many2one("hotel.room", "Room Name")

    cheacklist_line_ids = fields.One2many(
        "housekeeping.checklist.line", "room_id")

    @api.onchange('ref_name')
    def fetch_checklist(self):
        room_obj = self.env["hotel.room"]
        room_ids = room_obj.search([('name', '=', self.ref_name.name)])
        print(room_ids)
        for i in room_ids.cheack_line_ids:
            print("=========================", i.name)
            vals = {
                'name': i.name
            }
            print("================", vals)
            self.cheacklist_line_ids.write(vals)
            print("================", vals)


class Checklist(models.Model):
    _inherit = 'hotel.room'
    _description = 'Hotel Room Check List'

    cheack_line_ids = fields.One2many(
        "room.checklist.line", "room_no")
