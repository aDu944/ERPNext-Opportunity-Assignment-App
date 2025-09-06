frappe.pages['employee-opportunities'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'My Opportunities',
        single_column: true
    });
    
    // Create page content
    let $container = $(`
        <div class="opportunity-dashboard">
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-primary" id="total-open">0</h3>
                            <p class="text-muted">Open</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-warning" id="total-progress">0</h3>
                            <p class="text-muted">In Progress</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-danger" id="total-due">0</h3>
                            <p class="text-muted">Due Soon</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-success" id="total-quoted">0</h3>
                            <p class="text-muted">Quoted</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="filters-section mb-3">
                <div class="row">
                    <div class="col-md-3">
                        <select class="form-control" id="status-filter">
                            <option value="">All Status</option>
                            <option value="Open">Open</option>
                            <option value="In Progress">In Progress</option>
                            <option value="Quoted">Quoted</option>
                            <option value="Closed">Closed</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <select class="form-control" id="sort-filter">
                            <option value="expected_closing">Closing Date</option>
                            <option value="assignment_date">Assignment Date</option>
                            <option value="opportunity">Opportunity Name</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <button class="btn btn-primary" id="refresh-btn">
                            <i class="fa fa-refresh"></i> Refresh
                        </button>
                    </div>
                </div>
            </div>
            
            <div id="opportunities-list"></div>
        </div>
    `).appendTo(page.main);
    
    // Initialize
    let dashboard = new OpportunityDashboard(page, $container);
    dashboard.load();
};

class OpportunityDashboard {
    constructor(page, container) {
        this.page = page;
        this.container = container;
        this.setup_events();
    }
    
    setup_events() {
        this.container.find('#status-filter').on('change', () => this.load());
        this.container.find('#sort-filter').on('change', () => this.load());
        this.container.find('#refresh-btn').on('click', () => this.load());
    }
    
    load() {
        let status = this.container.find('#status-filter').val();
        let sort_by = this.container.find('#sort-filter').val();
        
        frappe.call({
            method: 'opportunity_assignment.opportunity_assignment.doctype.opportunity_assignment.opportunity_assignment.get_employee_assignments',
            args: {
                status: status,
                sort_by: sort_by
            },
            callback: (r) => {
                if (r.message) {
                    this.render_assignments(r.message);
                    this.update_stats(r.message);
                }
            }
        });
    }
    
    update_stats(assignments) {
        let stats = {
            open: 0,
            progress: 0,
            due_soon: 0,
            quoted: 0
        };
        
        assignments.forEach(a => {
            if (a.status === 'Open') stats.open++;
            if (a.status === 'In Progress') stats.progress++;
            if (a.status === '