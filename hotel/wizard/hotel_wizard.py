# See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from datetime import datetime, timedelta, date



class FolioReportWizard(models.TransientModel):
    _name = "folio.report.wizard"
    _rec_name = "date_start"
    _description = "Allow print folio report by date"

    date_start = fields.Datetime("Start Date")
    date_end = fields.Datetime("End Date")

    def print_report(self):
        data = {
            "ids": self.ids,
            "model": "hotel.folio",
            "form": self.read(["date_start", "date_end"])[0],
        }
        return self.env.ref("hotel.report_hotel_management").report_action(
            self, data=data
        )


class HotelFolioOrderCancel(models.TransientModel):
    _name = 'folio.order.cancel'
    _description = 'Hotel  Proforma Order Cancel'
    _inherit = ['mail.thread']

    remarks = fields.Text('Remarks')

    def tick_ok(self):
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['hotel.folio'].search([('id', '=', applicant_id)])
        today = date.today()
        current_date = today.strftime("%d/%m/%Y")
        current_user = self.env.user.name
        if active_id.state == 'draft':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.cancel_folio_order()
            active_id.write({'folio_cancel_remarks': text})
        if active_id.state == 'done':
            text = '[ ' + current_user + ' ]' + '[ ' + current_date + ' ]' + ' - ' + self.remarks + '\n'
            active_id.cancel_folio_order()
            active_id.write({'folio_cancel_remarks_2': text})
        return True
