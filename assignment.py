import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import re
from cryptography.fernet import Fernet
import base64
import hashlib

class PasswordManager:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Password Manager")
        self.window.geometry("800x500")
        self.window.configure(bg="#2b2b2b")
        
        self.cipher = None
        self.passwords = {}
        
        # Setup or login
        if not os.path.exists("master.key"):
            self.setup_master_password()
        else:
            self.login()
    
    def hash_password(self, password):
        """Create encryption key from password"""
        return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
    
    def setup_master_password(self):
        """First-time setup"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Setup Master Password")
        dialog.geometry("350x180")
        dialog.configure(bg="#2b2b2b")
        dialog.grab_set()
        
        tk.Label(dialog, text="Create Master Password", font=("Arial", 14, "bold"),
                bg="#2b2b2b", fg="white").pack(pady=20)
        
        tk.Label(dialog, text="Password:", bg="#2b2b2b", fg="white").pack()
        pwd1 = tk.Entry(dialog, show="*", width=30)
        pwd1.pack(pady=5)
        
        tk.Label(dialog, text="Confirm:", bg="#2b2b2b", fg="white").pack()
        pwd2 = tk.Entry(dialog, show="*", width=30)
        pwd2.pack(pady=5)
        
        def create():
            if not pwd1.get() or pwd1.get() != pwd2.get():
                messagebox.showerror("Error", "Passwords don't match or are empty!")
                return
            
            key = self.hash_password(pwd1.get())
            with open("master.key", 'wb') as f:
                f.write(key)
            
            self.cipher = Fernet(key)
            self.save_data()
            messagebox.showinfo("Success", "Master password created!")
            dialog.destroy()
            self.create_ui()
        
        tk.Button(dialog, text="Create", command=create, bg="#4CAF50", 
                 fg="white", font=("Arial", 11, "bold"), padx=20).pack(pady=15)
    
    def login(self):
        """Login screen"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Login")
        dialog.geometry("350x150")
        dialog.configure(bg="#2b2b2b")
        dialog.grab_set()
        
        tk.Label(dialog, text="Enter Master Password", font=("Arial", 14, "bold"),
                bg="#2b2b2b", fg="white").pack(pady=20)
        
        pwd_entry = tk.Entry(dialog, show="*", width=30)
        pwd_entry.pack(pady=5)
        
        def verify():
            key = self.hash_password(pwd_entry.get())
            with open("master.key", 'rb') as f:
                if key != f.read():
                    messagebox.showerror("Error", "Wrong password!")
                    return
            
            self.cipher = Fernet(key)
            self.load_data()
            dialog.destroy()
            self.create_ui()
        
        pwd_entry.bind('<Return>', lambda e: verify())
        tk.Button(dialog, text="Login", command=verify, bg="#2196F3",
                 fg="white", font=("Arial", 11, "bold"), padx=20).pack(pady=10)
    
    def save_data(self):
        """Save encrypted passwords"""
        data = json.dumps(self.passwords).encode()
        with open("passwords.enc", 'wb') as f:
            f.write(self.cipher.encrypt(data))
    
    def load_data(self):
        """Load encrypted passwords"""
        if os.path.exists("passwords.enc"):
            with open("passwords.enc", 'rb') as f:
                data = self.cipher.decrypt(f.read())
            self.passwords = json.loads(data.decode())
    
    def check_strength(self, pwd):
        """Check password strength"""
        score = sum([
            len(pwd) >= 8,
            len(pwd) >= 12,
            bool(re.search(r'[a-z]', pwd)),
            bool(re.search(r'[A-Z]', pwd)),
            bool(re.search(r'\d', pwd)),
            bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd))
        ])
        
        if score <= 2:
            return "Weak", "#f44336"
        elif score <= 4:
            return "Medium", "#ff9800"
        return "Strong", "#4CAF50"
    
    def create_ui(self):
        """Create main interface"""
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.window, bg="#1e1e1e", height=50)
        header.pack(fill=tk.X)
        tk.Label(header, text="🔐 Password Manager", font=("Arial", 16, "bold"),
                bg="#1e1e1e", fg="white").pack(pady=10)
        
        # Buttons
        btn_frame = tk.Frame(self.window, bg="#2b2b2b")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        buttons = [
            ("Add", self.add_password, "#4CAF50"),
            ("View", self.view_password, "#2196F3"),
            ("Edit", self.edit_password, "#ff9800"),
            ("Delete", self.delete_password, "#f44336")
        ]
        
        for text, cmd, color in buttons:
            tk.Button(btn_frame, text=text, command=cmd, bg=color, fg="white",
                     font=("Arial", 10, "bold"), padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Password list
        list_frame = tk.Frame(self.window, bg="#2b2b2b")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll = ttk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(list_frame, columns=("Website", "Username"), 
                                 show="headings", yscrollcommand=scroll.set)
        self.tree.heading("Website", text="Website")
        self.tree.heading("Username", text="Username")
        self.tree.column("Website", width=300)
        self.tree.column("Username", width=300)
        self.tree.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.tree.yview)
        
        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#363636", foreground="white",
                       fieldbackground="#363636")
        style.configure("Treeview.Heading", background="#1e1e1e", foreground="white",
                       font=("Arial", 10, "bold"))
        
        self.refresh_list()
    
    def refresh_list(self):
        """Refresh password list"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for site, data in self.passwords.items():
            self.tree.insert("", tk.END, values=(site, data.get('username', 'N/A')))
    
    def add_password(self):
        """Add new password"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Password")
        dialog.geometry("400x400")
        dialog.configure(bg="#2b2b2b")
        dialog.grab_set()
        
        fields = []
        labels = ["Website:", "Username:", "Password:", "Notes:"]
        
        for label in labels:
            tk.Label(dialog, text=label, bg="#2b2b2b", fg="white",
                    font=("Arial", 10)).pack(pady=5)
            entry = tk.Entry(dialog, width=40, show="*" if label == "Password:" else "")
            entry.pack(pady=5)
            fields.append(entry)
        
        # Strength indicator
        strength_label = tk.Label(dialog, text="Strength: N/A", bg="#2b2b2b",
                                 fg="gray", font=("Arial", 10, "bold"))
        strength_label.pack(pady=10)
        
        def update_strength(*args):
            pwd = fields[2].get()
            if pwd:
                strength, color = self.check_strength(pwd)
                strength_label.config(text=f"Strength: {strength}", fg=color)
        
        fields[2].bind('<KeyRelease>', update_strength)
        
        def save():
            site, user, pwd, notes = [f.get() for f in fields]
            
            if not site or not pwd:
                messagebox.showerror("Error", "Website and Password required!")
                return
            
            self.passwords[site] = {'username': user, 'password': pwd, 'notes': notes}
            self.save_data()
            self.refresh_list()
            messagebox.showinfo("Success", "Password saved!")
            dialog.destroy()
        
        tk.Button(dialog, text="Save", command=save, bg="#4CAF50", fg="white",
                 font=("Arial", 11, "bold"), padx=20, pady=5).pack(pady=15)
    
    def view_password(self):
        """View selected password"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a password first!")
            return
        
        site = self.tree.item(selection[0])['values'][0]
        data = self.passwords[site]
        
        dialog = tk.Toplevel(self.window)
        dialog.title(f"View - {site}")
        dialog.geometry("400x300")
        dialog.configure(bg="#2b2b2b")
        dialog.grab_set()
        
        info = [
            ("Website:", site),
            ("Username:", data.get('username', 'N/A')),
            ("Password:", data['password']),
            ("Notes:", data.get('notes', 'N/A'))
        ]
        
        for label, value in info:
            frame = tk.Frame(dialog, bg="#2b2b2b")
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            tk.Label(frame, text=label, bg="#2b2b2b", fg="#2196F3",
                    font=("Arial", 10, "bold"), width=12, anchor="w").pack(side=tk.LEFT)
            
            if label == "Password:":
                pwd_frame = tk.Frame(frame, bg="#2b2b2b")
                pwd_frame.pack(side=tk.LEFT)
                
                pwd_label = tk.Label(pwd_frame, text="••••••••", bg="#2b2b2b", fg="white")
                pwd_label.pack(side=tk.LEFT)
                
                def toggle(lbl=pwd_label, val=value):
                    lbl.config(text=val if lbl['text'] == "••••••••" else "••••••••")
                
                tk.Button(pwd_frame, text="Show", command=toggle, bg="#555",
                         fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
                
                def copy(val=value):
                    dialog.clipboard_clear()
                    dialog.clipboard_append(val)
                    messagebox.showinfo("Copied", "Password copied!")
                
                tk.Button(pwd_frame, text="Copy", command=copy, bg="#555",
                         fg="white", font=("Arial", 8)).pack(side=tk.LEFT)
            else:
                tk.Label(frame, text=value, bg="#2b2b2b", fg="white",
                        anchor="w").pack(side=tk.LEFT)
        
        tk.Button(dialog, text="Close", command=dialog.destroy, bg="#555",
                 fg="white", font=("Arial", 10), padx=20).pack(pady=20)
    
    def edit_password(self):
        """Edit selected password"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a password first!")
            return
        
        site = self.tree.item(selection[0])['values'][0]
        data = self.passwords[site]
        
        dialog = tk.Toplevel(self.window)
        dialog.title(f"Edit - {site}")
        dialog.geometry("400x350")
        dialog.configure(bg="#2b2b2b")
        dialog.grab_set()
        
        fields = []
        labels = ["Username:", "Password:", "Notes:"]
        values = [data.get('username', ''), data['password'], data.get('notes', '')]
        
        for label, value in zip(labels, values):
            tk.Label(dialog, text=label, bg="#2b2b2b", fg="white",
                    font=("Arial", 10)).pack(pady=5)
            entry = tk.Entry(dialog, width=40, show="*" if label == "Password:" else "")
            entry.insert(0, value)
            entry.pack(pady=5)
            fields.append(entry)
        
        # Strength indicator
        strength_label = tk.Label(dialog, text="", bg="#2b2b2b", font=("Arial", 10, "bold"))
        strength_label.pack(pady=10)
        
        def update_strength(*args):
            strength, color = self.check_strength(fields[1].get())
            strength_label.config(text=f"Strength: {strength}", fg=color)
        
        fields[1].bind('<KeyRelease>', update_strength)
        update_strength()
        
        def save():
            user, pwd, notes = [f.get() for f in fields]
            if not pwd:
                messagebox.showerror("Error", "Password required!")
                return
            
            self.passwords[site] = {'username': user, 'password': pwd, 'notes': notes}
            self.save_data()
            self.refresh_list()
            messagebox.showinfo("Success", "Password updated!")
            dialog.destroy()
        
        tk.Button(dialog, text="Update", command=save, bg="#ff9800", fg="white",
                 font=("Arial", 11, "bold"), padx=20, pady=5).pack(pady=15)
    
    def delete_password(self):
        """Delete selected password"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a password first!")
            return
        
        site = self.tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete password for '{site}'?"):
            del self.passwords[site]
            self.save_data()
            self.refresh_list()
            messagebox.showinfo("Success", "Password deleted!")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PasswordManager()
    app.run()