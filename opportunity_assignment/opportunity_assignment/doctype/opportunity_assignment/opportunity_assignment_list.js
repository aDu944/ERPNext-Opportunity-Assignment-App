frappe.listview_settings['Opportunity Assignment'] = {
    add_fields: ['status', 'expected_closing', 'employee_name'],
    
    get_indicator: function(doc) {
        if (doc.status === 'Closed') {
            return [__('Closed'), 'gray', 'status,=,Closed'];
        } else if (doc.status === 'Quoted') {
            return [__('Quoted'), 'green', 'status,=,Quoted'];
        } else if (doc.status === 'In Progress') {
            return [__('In Progress'), 'orange', 'status,=,In Progress'];
        } else if (doc.expected_closing) {
            const today = frappe.datetime.get_today();
            const closing = doc.expected_closing;
            const diff = frappe.datetime.get_diff(closing, today);
            
            if (diff < 0) {
                return [__('Overdue'), 'red', 'expected_closing,<,Today'];
            } else if (diff === 0) {
                return [__('Due Today'), 'red', 'expected_closing,=,Today'];
            } else if (diff <= 3) {
                return [__('Due Soon'), 'orange', 'expected_closing,<=,' + frappe.datetime.add_days(today, 3)];
            }
        }
        return [__('Open'), 'blue', 'status,=,Open'];
    },
    
    onload: function(listview) {
        listview.page.add_menu_item(__('Send Bulk Reminders'), function() {
            frappe.call({
                method: 'opportunity_assignment.opportunity_assignment.tasks.send_daily_reminders',
                callback: function(r) {
                    frappe.show_alert({
                        message: __('Reminders sent successfully'),
                        indicator: 'green'
                    });
                }
            });
        });
    }
};