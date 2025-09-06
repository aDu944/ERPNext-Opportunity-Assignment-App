import frappe
import unittest
from frappe.utils import nowdate, add_days

class TestOpportunityAssignment(unittest.TestCase):
    def setUp(self):
        # Create test employee
        if not frappe.db.exists("Employee", "TEST-EMP-001"):
            self.employee = frappe.get_doc({
                "doctype": "Employee",
                "employee_name": "Test Employee",
                "company": frappe.defaults.get_global_default("company"),
                "personal_email": "test@example.com"
            }).insert()
        else:
            self.employee = frappe.get_doc("Employee", "TEST-EMP-001")
        
        # Create test opportunity
        self.opportunity = frappe.get_doc({
            "doctype": "Opportunity",
            "opportunity_type": "Sales",
            "party_type": "Customer",
            "party_name": frappe.db.get_value("Customer", {"customer_type": "Company"}, "name"),
            "expected_closing": add_days(nowdate(), 7)
        }).insert()
    
    def test_assignment_creation(self):
        assignment = frappe.get_doc({
            "doctype": "Opportunity Assignment",
            "opportunity": self.opportunity.name,
            "employee": self.employee.name,
            "expected_closing": self.opportunity.expected_closing,
            "status": "Open"
        }).insert()
        
        self.assertEqual(assignment.employee_name, self.employee.employee_name)
        self.assertEqual(assignment.employee_email, self.employee.personal_email)
    
    def tearDown(self):
        frappe.delete_doc("Opportunity", self.opportunity.name)