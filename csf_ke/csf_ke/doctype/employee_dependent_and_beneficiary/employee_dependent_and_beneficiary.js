// Copyright (c) 2024, Navari Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Dependent and Beneficiary", {
  refresh: function (frm) {
    calculate_and_set_age(frm);
  },
  dob: function (frm) {
    calculate_and_set_age(frm);
  },
});

function calculate_and_set_age(frm) {
  if (frm.doc.dob) {
    const dob = frappe.datetime.str_to_obj(frm.doc.dob);
    const today = new Date();
    let age = today.getFullYear() - dob.getFullYear();

    const hasBirthdayPassed =
      today.getMonth() > dob.getMonth() ||
      (today.getMonth() === dob.getMonth() && today.getDate() >= dob.getDate());

    if (!hasBirthdayPassed) {
      age -= 1;
    }
    frm.set_value("age", age);
  } else {
    frm.set_value("age", null);
  }
}
