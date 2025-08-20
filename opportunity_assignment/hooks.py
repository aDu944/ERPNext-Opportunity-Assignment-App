from . import __version__ as app_version

app_name = "opportunity_assignment"
app_title = "Opportunity Assignment"
app_publisher = "Your Company"
app_description = "Manage opportunity assignments with automated reminders"
app_icon = "octicon octicon-briefcase"
app_color = "blue"
app_email = "your-email@company.com"
app_license = "MIT"

# Includes in <head>
app_include_css = "/assets/opportunity_assignment/css/opportunity_assignment.css"
app_include_js = "/assets/opportunity_assignment/js/opportunity_custom.js"

# Include custom scripts for specific doctypes
doctype_js = {
    "Opportunity": "public/js/opportunity_custom.js"
}

# Document Events
doc_events = {
    "Opportunity": {
        "after_insert": "opportunity_assignment.opportunity_assignment.doctype.opportunity_assignment.opportunity_assignment.create_assignments_from_opportunity",
        "on_update": "opportunity_assignment.opportunity_assignment.doctype.opportunity_assignment.opportunity_assignment.update_assignments_from_opportunity"
    }
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "opportunity_assignment.opportunity_assignment.tasks.send_daily_reminders"
    ],
    "hourly": [
        "opportunity_assignment.opportunity_assignment.tasks.check_overdue_assignments"
    ]
}

# Permissions
permission_query_conditions = {
    "Opportunity Assignment": "opportunity_assignment.opportunity_assignment.doctype.opportunity_assignment.opportunity_assignment.get_permission_query_conditions"
}

has_permission = {
    "Opportunity Assignment": "opportunity_assignment.opportunity_assignment.doctype.opportunity_assignment.opportunity_assignment.has_permission"
}
