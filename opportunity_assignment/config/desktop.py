from frappe import _

def get_data():
    return [
        {
            "module_name": "Opportunity Assignment",
            "category": "Modules",
            "label": _("Opportunity Assignment"),
            "color": "#1e4c8a",
            "icon": "octicon octicon-briefcase",
            "type": "module",
            "description": "Manage opportunity assignments and track quotation tasks",
            "onboard_present": 1
        }
    ]