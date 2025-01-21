from frappe.core.doctype.file.file import File as OriginalFile
import frappe

class File(OriginalFile):

    def is_downloadable(self):
        if not self.file_url.endswith('.csv') or frappe.local.session.user == 'Guest':
            return super().is_downloadable()
        # User is authenticated, so can access files
        return True