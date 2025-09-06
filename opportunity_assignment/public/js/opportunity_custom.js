frappe.ui.form.on('Opportunity', {
    refresh: function(frm) {
        // Add button to view assignments
        if (!frm.doc.__islocal && frm.doc.custom_resp_eng) {
            frm.add_custom_button(__('View Assignments'), function() {
                frappe.route_options = {
                    'opportunity': frm.doc.name
                };
                frappe.set_route('List', 'Opportunity Assignment');
            }, __('Actions'));
            
            // Show assignment count
            frappe.call({
                method: 'frappe.client.get_count',
                args: {
                    doctype: 'Opportunity Assignment',
                    filters: {
                        opportunity: frm.doc.name
                    }
                },
                callback: function(r) {
                    if (r.message) {
                        frm.dashboard.add_indicator(
                            __('Assignments: {0}', [r.message]),
                            'blue'
                        );
                    }
                }
            });
        }
    },
    
    custom_resp_eng: function(frm) {
        // Trigger assignment creation on change
        if (frm.doc.custom_resp_eng && !frm.doc.__islocal) {
            frappe.show_alert({
                message: __('Assignments will be created after saving'),
                indicator: 'blue'
            });
        }
    }
});