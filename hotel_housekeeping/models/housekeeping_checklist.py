from odoo import api, fields, models, _


class HousekeepingChecklistLine(models.Model):
    _name = 'housekeeping.checklist.line'
    _description = 'House Keeping Checklist Line'

    name = fields.Char(string='Name')
    room_id = fields.Many2one('hotel.folio', string='Company')
    true = fields.Boolean('True')
    false = fields.Boolean('False')
    remarks = fields.Char(string='Remarks')
    things_selection = fields.Selection([
        ('available', 'Available'),
        ('non_available', 'Non Available')],
        string='Things',
    )

    def click_yes(self):
        self.write({
            'things_selection': 'available', })
        room_obj = self.env["hotel.room"].search([('name', '=', self.room_id.ref_name.name)])
        for room in room_obj.cheack_line_ids:
            if self.name == room.name:
                room.write({
                    'things_selection': 'available'
                })

    def click_no(self):
        self.write({
            'things_selection': 'non_available', })
        room_obj = self.env["hotel.room"].search([('name', '=', self.room_id.ref_name.name)])
        for room in room_obj.cheack_line_ids:
            if self.name == room.name:
                room.write({
                    'things_selection': 'non_available'
                })


class RoomChecklistLine(models.Model):
    _name = 'room.checklist.line'
    _description = 'Room Checklist Line'

    name = fields.Char(string='Name')
    room_no = fields.Many2one('hotel.room', string='Company')
    remarks = fields.Char(string='Remarks')
    things_selection = fields.Selection([
        ('available', 'Available'),
        ('non_available', 'Non Available')],
        string='Things',
    )


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
        list = [(5, 0, 0)]
        for i in room_ids.cheack_line_ids:
            vals = {
                'name': i.name,
                'things_selection' : i.things_selection
            }
            list.append((0, 0, vals))
        self.cheacklist_line_ids = list


class Checklist(models.Model):
    _inherit = 'hotel.room'
    _description = 'Hotel Room Check List'

    cheack_line_ids = fields.One2many(
        "room.checklist.line", "room_no")
