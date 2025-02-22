# ERPNext Country Specific Functionality for Kenya
---

This application extends ERPNext to support country-specific functionality for Kenya. It includes tax compliance features, TIMs integration, localized financial reporting, and enhancements tailored to Kenyan businesses.

## Includes:

### Kenya Payroll Reports

These reports help businesses comply with payroll regulations and generate required documentation for statutory deductions.

- [P9A Tax Deduction Card](csf_ke/docs/reports/kenya_p9_tax_report.md) - Summarizes PAYE tax deductions for employees.
- [P10 Tax Report](csf_ke/docs/reports/kenya_p10_tax_report.md) - Monthly tax return report for employers.
- NSSF Report - Contributions report for the National Social Security Fund.
- NHIF Report - Health insurance contributions report.
- HELB Report - Student loan repayment deductions report.
- Bank Payroll Advice Report - Generates bank instructions for salary processing.
- Payroll Register Report - Provides a detailed breakdown of payroll transactions.

### Tax Reports

- [Sales Tax Report](csf_ke/docs/reports/kenya_sales_tax_report.md)
- [Purchase Tax Report](csf_ke/docs/reports/kenya_purchase_tax_report.md)

### Tax Compliance

To meet Kenyan tax regulations, the app includes custom fields and integrations:
 - [Documentation](csf_ke/docs/features/tims_integration.md)

- Custom ETR fields in Sales and Purchase invoices - Captures TIMs invoice details for tax compliance.
- TIMs HSCode - Links items to Harmonized System codes for proper tax classification.
- [VAT Withholding](csf_ke/docs/doctypes/vat_withholding.md) - Easy importation of paid withholding from kra website into ERPNext.

#### Important Note
For the TIMs Parser integration we are using a trusted partner. Please contact them for installation details at: [Cecypo](https://docs.cecypo.tech/s/kb/doc/erpnext-O7U5xeE9DN)

### Other Features

- [Selling Item Price Margin](csf_ke/docs/doctypes/selling_item_price_margin.md) - Helps businesses determine profitability on sales items.

---

## How to Install 🛠️

### Manual Installation/Self Hosting

To install the app, [Setup, Initialise, and run a Frappe Bench instance](https://frappeframework.com/docs/user/en/installation).

Once the instance is up and running, add the application to the environment by running the command below in an active Bench terminal:

```sh
bench get-app https://github.com/navariltd/navari_csf_ke.git
```

followed by:

```sh
bench --site <your.site.name.here> install-app csf_ke
```


### FrappeCloud Installation ☁️

Installing on [FrappeCloud](https://frappecloud.com/docs/introduction) can be achieved after setting up a Bench instance and a site. The app can then be added using the _Add App_ button in the _App_ tab of the bench and referencing this repository by using the _Install from GitHub_ option if you are not able to search for the app.
