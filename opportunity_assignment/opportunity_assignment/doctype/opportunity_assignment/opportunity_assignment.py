import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, getdate, now_datetime, formatdate
from frappe import _
import json

class OpportunityAssignment(Document):
    def validate(self):
        self.set_employee_details()
        self.validate_dates()
        
    def set_employee_details(self):
        if self.employee:
            employee = frappe.get_doc("Employee", self.employee)
            self.employee_name = employee.employee_name
            self.employee_email = employee.personal_email or employee.company_email
            
            if not self.employee_email:
                frappe.throw(_("Employee {0} does not have an email address").format(self.employee))
    
    def validate_dates(self):
        if self.expected_closing and getdate(self.expected_closing) < getdate(nowdate()):
            frappe.msgprint(_("Expected closing date is in the past"), alert=True)
    
    def after_insert(self):
        self.send_assignment_email()
    
    def send_assignment_email(self):
        """Send initial assignment email to employee"""
        if not self.employee_email:
            return
        
        opportunity = frappe.get_doc("Opportunity", self.opportunity)
        
        # Render email template
        items_html = self.get_items_html()
        
        args = {
            "employee_name": self.employee_name,
            "opportunity_name": opportunity.opportunity_name or self.opportunity,
            "customer": opportunity.party_name,
            "closing_date": formatdate(self.expected_closing),
            "items_html": items_html,
            "assignment_link": frappe.utils.get_url_to_form("Opportunity Assignment", self.name)
        }
        
        frappe.sendmail(
            recipients=[self.employee_email],
            subject=_("New Opportunity Assignment: {0}").format(opportunity.opportunity_name or self.opportunity),
            template="opportunity_assignment",
            args=args,
            delayed=False
        )
        
        frappe.db.set_value("Opportunity Assignment", self.name, "email_sent", 1, update_modified=False)
    
    def get_items_html(self):
        """Generate HTML for items list"""
        if not self.items_to_quote:
            return "<p>No specific items assigned yet.</p>"
        
        html = "<table style='width: 100%; border-collapse: collapse;'>"
        html += "<thead><tr style='background-color: #f0f0f0;'>"
        html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Item</th>"
        html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Quantity</th>"
        html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>UOM</th>"
        html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Description</th>"
        html += "</tr></thead><tbody>"
        
        for item in self.items_to_quote:
            html += "<tr>"
            html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{item.item_name or item.item_code}</td>"
            html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{item.quantity}</td>"
            html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{item.uom or '-'}</td>"
            html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{item.description or '-'}</td>"
            html += "</tr>"
        
        html += "</tbody></table>"
        return html
    
    def send_reminder(self, days_before):
        """Send reminder email"""
        if not self.employee_email or self.status in ["Quoted", "Closed"]:
            return
        
        opportunity = frappe.get_doc("Opportunity", self.opportunity)
        
        # Check if reminder already sent
        reminder_field = f"reminder_{days_before}_days" if days_before > 0 else "reminder_closing_date"
        if self.get(reminder_field):
            return
        
        subject_suffix = f"{days_before} days remaining" if days_before > 0 else "Due Today!"
        
        args = {
            "employee_name": self.employee_name,
            "opportunity_name": opportunity.opportunity_name or self.opportunity,
            "customer": opportunity.party_name,
            "closing_date": formatdate(self.expected_closing),
            "days_remaining": days_before,
            "items_html": self.get_items_html(),
            "assignment_link": frappe.utils.get_url_to_form("Opportunity Assignment", self.name)
        }
        
        frappe.sendmail(
            recipients=[self.employee_email],
            subject=_("Reminder: {0} - {1}").format(opportunity.opportunity_name or self.opportunity, subject_suffix),
            template="opportunity_reminder",
            args=args,
            delayed=False
        )
        
        # Mark reminder as sent
        frappe.db.set_value("Opportunity Assignment", self.name, reminder_field, 1, update_modified=False)

@frappe.whitelist()
def create_assignments_from_opportunity(doc, method=None):
    """Create assignments when opportunity is created/updated"""
    if isinstance(doc, str):
        doc = frappe.get_doc("Opportunity", doc)
    
    if not doc.custom_resp_eng:
        return
    
    # Parse the TableMultiSelect field
    try:
        if isinstance(doc.custom_resp_eng, str):
            selected_employees = json.loads(doc.custom_resp_eng)
        else:
            selected_employees = doc.custom_resp_eng
    except:
        return
    
    # Get existing assignments
    existing = frappe.get_all(
        "Opportunity Assignment",
        filters={"opportunity": doc.name},
        pluck="employee"
    )
    
    for employee_id in selected_employees:
        if employee_id not in existing:
            assignment = frappe.new_doc("Opportunity Assignment")
            assignment.opportunity = doc.name
            assignment.employee = employee_id
            assignment.expected_closing = doc.expected_closing
            assignment.status = "Open"
            assignment.assignment_date = now_datetime()
            
            # Copy items if they exist
            if hasattr(doc, "items"):
                for item in doc.items:
                    assignment.append("items_to_quote", {
                        "item_code": item.item_code,
                        "quantity": item.qty,