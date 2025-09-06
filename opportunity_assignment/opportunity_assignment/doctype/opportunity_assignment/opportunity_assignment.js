frappe.ui.form.on('Opportunity Assignment', {
    refresh: function(frm) {
        // Add custom buttons
        if (!frm.doc.__islocal && frm.doc.status !== 'Closed') {
            frm.add_custom_button(__('Send Reminder'), function() {
                frappe.call({
                    method: 'send_reminder',
                    doc: frm.doc,
                    args: {
                        days_before: 0
                    },
                    callback: function(r) {
                        frappe.show_alert({
                            message: __('Reminder email sent'),
                            indicator: 'green'
                        });
                    }
                });
            });
            
            if (frm.doc.status === 'Open') {
                frm.add_custom_button(__('Mark In Progress'), function() {
                    frm.set_value('status', 'In Progress');
                    frm.save();
                });
            }
            
            if (frm.doc.status === 'In Progress') {
                frm.add_custom_button(__('Mark as Quoted'), function() {
                    frm.set_value('status', 'Quoted');
                    frm.save();
                });
            }
        }
        
        // Color code based on days remaining
        if (frm.doc.expected_closing) {
            let closing = new Date(frm.doc.expected_closing);
            let today = new Date();
            let days = Math.ceil((closing - today) / (1000 * 60 * 60 * 24));
            
            let indicator = 'blue';
            let message = '';
            
            if (days < 0) {
                indicator = 'red';
                message = __('Overdue by {0} days', [Math.abs(days)]);
            } else if (days === 0) {
                indicator = 'red';
                message = __('Due Today!');
            } else if (days <= 3) {
                indicator = 'orange';
                message = __('Due in {0} days', [days]);
            } else if (days <= 7) {
                indicator = 'yellow';
                message = __('Due in {0} days', [days]);
            } else {
                indicator = 'green';
                message = __('Due in {0} days', [days]);
            }
            
            frm.dashboard.add_indicator(message, indicator);
        }
    },
    
    employee: function(frm) {
        if (frm.doc.employee) {
            frappe.db.get_value('Employee', frm.doc.employee, 
                ['employee_name', 'personal_email', 'company_email'], 
                function(r) {
                    if (r) {
                        frm.set_value('employee_name', r.employee_name);
                        frm.set_value('employee_email', r.personal_email || r.company_email);
                    }
                }
            );
        }
    },
    
    opportunity: function(frm) {
        if (frm.doc.opportunity) {
            frappe.model.with_doc('Opportunity', frm.doc.opportunity, function() {
                let opp = frappe.model.get_doc('Opportunity', frm.doc.opportunity);
                frm.set_value('expected_closing', opp.expected_closing);
                
                // Copy items if available
                if (opp.items && opp.items.length > 0) {
                    frm.clear_table('items_to_quote');
                    opp.items.forEach(function(item) {
                        let row = frm.add_child('items_to_quote');
                        row.item_code = item.item_code;
                        row.item_name = item.item_name;
                        row.quantity = item.qty;
                        row.uom = item.uom;
                        row.description = item.description;
                    });
                    frm.refresh_field('items_to_quote');
                }
            });
        }
    }
});