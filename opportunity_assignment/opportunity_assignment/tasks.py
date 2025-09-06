import frappe
from frappe.utils import nowdate, getdate, add_days

def send_daily_reminders():
    """Send daily reminder emails for upcoming deadlines"""
    today = getdate(nowdate())
    
    # Get all open assignments
    assignments = frappe.get_all(
        "Opportunity Assignment",
        filters={
            "status": ["in", ["Open", "In Progress"]],
            "expected_closing": ["is", "set"]
        },
        fields=["name", "expected_closing", "reminder_7_days", 
                "reminder_3_days", "reminder_1_day", "reminder_closing_date"]
    )
    
    for assignment in assignments:
        closing_date = getdate(assignment.expected_closing)
        days_until = (closing_date - today).days
        
        doc = frappe.get_doc("Opportunity Assignment", assignment.name)
        
        # Send appropriate reminders
        if days_until == 7 and not assignment.reminder_7_days:
            doc.send_reminder(7)
        elif days_until == 3 and not assignment.reminder_3_days:
            doc.send_reminder(3)
        elif days_until == 1 and not assignment.reminder_1_day:
            doc.send_reminder(1)
        elif days_until == 0 and not assignment.reminder_closing_date:
            doc.send_reminder(0)
    
    frappe.db.commit()

def check_overdue_assignments():
    """Mark assignments as overdue if past closing date"""
    overdue = frappe.get_all(
        "Opportunity Assignment",
        filters={
            "status": ["in", ["Open", "In Progress"]],
            "expected_closing": ["<", nowdate()]
        },
        pluck="name"
    )
    
    for name in overdue:
        frappe.db.set_value("Opportunity Assignment", name, "is_overdue", 1)
    
    if overdue:
        frappe.db.commit()