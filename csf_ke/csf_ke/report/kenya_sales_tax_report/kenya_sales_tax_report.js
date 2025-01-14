// Copyright (c) 2022, Navari Limited and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Kenya Sales Tax Report"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"to_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"is_return",
			"label": __("Is Return"),
			"fieldtype": "Select",
			"options": ["","Is Return","Normal Sales Invoice"],
			"default": "",
			"reqd": 0,
			"width": "100px"
		},
		{
			"fieldname":"tax_template",
			"label": __("Tax Template"),
			"fieldtype": "Link",
			"options": "Item Tax Template",
			"reqd": 0,
			"width": "100px"
		}
	],
    "onload": function(report) {
        report.page.add_action_icon('bi bi-download', function() {
            // frappe.msgprint(__('This is a custom action!!!'))
            frappe.call({
                method: "csf_ke.csf_ke.report.kenya_sales_tax_report.kenya_sales_tax_report.download_custom_csv_format",
                args: {
                    company: report.get_filter_value("company"),
                    from_date: report.get_filter_value("from_date"),
                    to_date: report.get_filter_value("to_date")
                },
                callback: function(response) {
                    if (response.message) {
                        const fileLinks = Object.entries(response.message).map(([template, fileUrl]) => {
                            return `<a href="${fileUrl}" target="_blank">${template} Sales Report</a>`;
                        });

                        // Display links in a modal
                        frappe.msgprint({
                            title: __('CSV Download Links'),
                            message: fileLinks.join('<br>'),
                            indicator: 'green'
                        });
                    } else {
                        frappe.msgprint(__('No files were generated'));
                    }
                },
                error: function() {
                    frappe.msgprint(__('An error occured while generating the CSV files.'));
                }
            });
        });
    }
};
