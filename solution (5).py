import tkinter as tk
from tkinter import ttk, messagebox
import re
import mysql.connector

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

DB_PARAMS = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'contacts_db'
}

class ContactApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")
        self.root.geometry("750x550")
        self.init_db()
        self.build_ui()
        self.refresh_list()

    def init_db(self):
        try:
            self.conn = mysql.connector.connect(**DB_PARAMS)
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Contact (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    category VARCHAR(50),
                    notes TEXT
                );
            """)
            self.conn.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def build_ui(self):
        form_frame = ttk.LabelFrame(self.root, text="Contact Details")
        form_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.ent_name = ttk.Entry(form_frame, width=30)
        self.ent_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Email:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.ent_email = ttk.Entry(form_frame, width=30)
        self.ent_email.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ent_phone = ttk.Entry(form_frame, width=30)
        self.ent_phone.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Category:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.cmb_category = ttk.Combobox(form_frame, values=["Faculty", "Student", "Staff", "Industry"], width=28)
        self.cmb_category.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Notes:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")
        self.txt_notes = tk.Text(form_frame, width=60, height=3)
        self.txt_notes.grid(row=2, column=1, columnspan=3, padx=5, pady=5)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Add", command=self.add_contact).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update", command=self.update_contact).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_contact).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_fields).pack(side="left", padx=5)

        search_frame = ttk.LabelFrame(self.root, text="Search & Filter")
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Query:").pack(side="left", padx=5)
        self.ent_search = ttk.Entry(search_frame, width=30)
        self.ent_search.pack(side="left", padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_contacts).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Reset", command=self.refresh_list).pack(side="left", padx=5)

        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Email", "Phone", "Category"), show="headings")
        for col in ("ID", "Name", "Email", "Phone", "Category"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def validate_inputs(self):
        name = self.ent_name.get().strip()
        email = self.ent_email.get().strip()
        if not name or not email:
            messagebox.showwarning("Validation Error", "Name and Email are required.")
            return False
        if not EMAIL_REGEX.match(email):
            messagebox.showwarning("Validation Error", "Invalid Email format.")
            return False
        return True

    def add_contact(self):
        if not self.validate_inputs():
            return
        name = self.ent_name.get().strip()
        email = self.ent_email.get().strip()
        phone = self.ent_phone.get().strip()
        category = self.cmb_category.get().strip()
        notes = self.txt_notes.get("1.0", tk.END).strip()

        try:
            self.cursor.execute("""
                INSERT INTO Contact (name, email, phone, category, notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, email, phone, category, notes))
            self.conn.commit()
            self.refresh_list()
            self.clear_fields()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Email address already exists.")

    def update_contact(self):
        selected = self.tree.selection()
        if not selected:
            return
        if not self.validate_inputs():
            return

        contact_id = self.tree.item(selected[0])['values'][0]
        try:
            self.cursor.execute("""
                UPDATE Contact
                SET name=%s, email=%s, phone=%s, category=%s, notes=%s
                WHERE id=%s
            """, (self.ent_name.get().strip(), self.ent_email.get().strip(),
                  self.ent_phone.get().strip(), self.cmb_category.get().strip(),
                  self.txt_notes.get("1.0", tk.END).strip(), contact_id))
            self.conn.commit()
            self.refresh_list()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Email address conflict.")

    def delete_contact(self):
        selected = self.tree.selection()
        if not selected:
            return
        contact_id = self.tree.item(selected[0])['values'][0]
        self.cursor.execute("DELETE FROM Contact WHERE id=%s", (contact_id,))
        self.conn.commit()
        self.refresh_list()
        self.clear_fields()

    def search_contacts(self):
        query = f"%{self.ent_search.get().strip()}%"
        self.cursor.execute("""
            SELECT id, name, email, phone, category FROM Contact
            WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
            ORDER BY name ASC
        """, (query, query, query))
        self.render_rows(self.cursor.fetchall())

    def refresh_list(self):
        self.cursor.execute("SELECT id, name, email, phone, category FROM Contact ORDER BY name ASC")
        self.render_rows(self.cursor.fetchall())

    def render_rows(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        contact_id = self.tree.item(selected[0])['values'][0]
        self.cursor.execute("SELECT name, email, phone, category, notes FROM Contact WHERE id=%s", (contact_id,))
        row = self.cursor.fetchone()
        if row:
            self.ent_name.delete(0, tk.END)
            self.ent_name.insert(0, row[0])
            self.ent_email.delete(0, tk.END)
            self.ent_email.insert(0, row[1])
            self.ent_phone.delete(0, tk.END)
            self.ent_phone.insert(0, row[2])
            self.cmb_category.set(row[3])
            self.txt_notes.delete("1.0", tk.END)
            self.txt_notes.insert("1.0", row[4])

    def clear_fields(self):
        self.ent_name.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.ent_phone.delete(0, tk.END)
        self.cmb_category.set("")
        self.txt_notes.delete("1.0", tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    app = ContactApp(root)
    root.mainloop()
