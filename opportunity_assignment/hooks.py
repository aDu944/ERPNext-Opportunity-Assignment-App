from . import __version__ as app_version

app_name = "opportunity_assignment"
app_title = "Opportunity Assignment"
app_publisher = "ALKHORA"
app_description = "Auto assignment of opportunities with notifications"
app_email = "erp@alkhora.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/opportunity_assignment/css/opportunity.css"
app_include_js = "/assets/opportunity_assignment/js/opportunity.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "opportunity_assignment/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Opportunity" : "public/js/opportunity.js"
}

# DocType Class
# ---------------
# Override standard doctype classes
# from opportunity_assignment.opportunity_assignment.doctype.opportunity_assignment.opportunity_assignment import OpportunityAssignment

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
    "Opportunity": {
        "after_insert": "opportunity_assignment.api.after_opportunity_insert",
        "validate": "opportunity_assignment.api.validate_opportunity",
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "opportunity_assignment.api.send_daily_reminders"
    ],
    "all": [
        "opportunity_assignment.api.send_reminder_notifications"
    ]
}

# Fixtures
# --------
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Opportunity Assignment"]]},
    {"dt": "Client Script", "filters": [["module", "=", "Opportunity Assignment"]]},
]
