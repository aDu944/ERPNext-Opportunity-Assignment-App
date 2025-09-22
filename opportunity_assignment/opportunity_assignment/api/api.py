import frappe
from frappe import _
from frappe.utils import getdate, add_days, nowdate, get_url

@frappe.whitelist()
def after_opportunity_insert(doc, method=None):
    """After Opportunity is inserted, assign to employee and send notification"""
    try:
        # Assign opportunity to employee
        assign_to_employee(doc)
        
        # Send initial assignment email
        send_assignment_notification(doc)
        
    except Exception as e:
        frappe.log_error(f"Error in after_opportunity_insert: {str(e)}")

def assign_to_employee(doc):
    """Assign opportunity to an employee based on your logic"""
    # Example: Round-robin assignment or based on territory
    employees = frappe.get_all("Employee", 
        filters={"department": "Sales", "status": "Active"}, 
        fields=["name", "user_id"]
    )
    
    if employees:
        # Simple round-robin - get the employee with least assignments
        assigned_employee = get_employee_with_least_assignments(employees)
        
        if assigned_employee:
            doc.assigned_to = assigned_employee.user_id
            doc.save()
            frappe.db.commit()

def get_employee_with_least_assignments(employees):
    """Get employee with least open opportunities"""
    employee_assignments = {}
    
    for emp in employees:
        if emp.user_id:
            count = frappe.db.count("Opportunity", {
                "assigned_to": emp.user_id,
                "status": ["!=", "Lost"]
            })
            employee_assignments[emp.user_id] = count
    
    if employee_assignments:
        min_employee = min(employee_assignments, key=employee_assignments.get)
        return next(emp for emp in employees if emp.user_id == min_employee)
    
    return employees[0] if employees else None

def send_assignment_notification(doc):
    """Send email notification when opportunity is assigned"""
    if not doc.assigned_to:
        return
        
    subject = _("New Opportunity Assigned: {0}").format(doc.name)
    message = f"""
    <p>Hello,</p>
    
    <p>A new opportunity has been assigned to you:</p>
    
    <p><strong>Opportunity:</strong> {doc.name}<br>
    <strong>Customer:</strong> {doc.customer_name}<br>
    <strong>Closing Date:</strong> {doc.closed_by}<br>
    <strong>Opportunity From:</strong> {doc.opportunity_from}</p>
    
    <p>Please review the opportunity and add the required items for quotation.</p>
    
    <p><a href="{get_url_to_form(doc.doctype, doc.name)}">Open Opportunity</a></p>
    
    <p>Best regards,<br>Sales Team</p>
    """
    
    frappe.sendmail(
        recipients=[doc.assigned_to],
        subject=subject,
        message=message,
        reference_doctype=doc.doctype,
        reference_name=doc.name
    )

def send_daily_reminders():
    """Send daily reminder emails for opportunities due in 7, 3, 1, 0 days"""
    try:
        opportunities = get_opportunities_due_for_reminder()
        
        for opportunity in opportunities:
            send_reminder_notification(opportunity)
            
    except Exception as e:
        frappe.log_error(f"Error in send_daily_reminders: {str(e)}")

def get_opportunities_due_for_reminder():
    """Get opportunities that need reminders today"""
    today = getdate()
    reminder_days = [0, 1, 3, 7]  # Days before closing date
    
    opportunities = []
    
    for days in reminder_days:
        target_date = add_days(today, days)
        
        opps = frappe.get_all("Opportunity",
            filters={
                "closed_by": target_date,
                "status": "Open",
                "assigned_to": ["!=", ""]
            },
            fields=["name", "assigned_to", "customer_name", "closed_by"]
        )
        
        opportunities.extend(opps)
    
    return opportunities

def send_reminder_notification(opportunity):
    """Send reminder notification for an opportunity"""
    days_until_due = (getdate(opportunity.closed_by) - getdate()).days
    
    subject = _("Reminder: Opportunity {0} due in {1} days").format(
        opportunity.name, days_until_due
    )
    
    message = f"""
    <p>Hello,</p>
    
    <p>This is a reminder for your opportunity:</p>
    
    <p><strong>Opportunity:</strong> {opportunity.name}<br>
    <strong>Customer:</strong> {opportunity.customer_name}<br>
    <strong>Due Date:</strong> {opportunity.closed_by}<br>
    <strong>Days Remaining:</strong> {days_until_due}</p>
    
    <p>Please ensure all required items are added and quotation is prepared.</p>
    
    <p><a href="{get_url_to_form('Opportunity', opportunity.name)}">Open Opportunity</a></p>
    
    <p>Best regards,<br>Sales Team</p>
    """
    
    frappe.sendmail(
        recipients=[opportunity.assigned_to],
        subject=subject,
        message=message,
        reference_doctype="Opportunity",
        reference_name=opportunity.name
    )

def get_url_to_form(doctype, name):
    """Get absolute URL to document"""
    return get_url(f"/app/{frappe.scrub(doctype)}/{name}")
