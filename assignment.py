import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import re
from cryptography.fernet import Fernet
import base64
import hashlib

# ── Design Tokens ──────────────────────────────────────────────
BG       = "#0d0f14"
SURFACE  = "#161a24"
CARD     = "#1e2330"
BORDER   = "#2a3045"
ACCENT   = "#4f8ef7"
ACCENT2  = "#6ee7b7"
DANGER   = "#f75555"
WARNING  = "#f7a355"
TEXT     = "#e8eaf0"
MUTED    = "#6b7280"
FONT     = "Consolas"

class SecurityManager: 
    """Handles hashing, encryption, and decryption operations."""

    def __init__(self, key=None):
        self.key = key
        self.cipher = Fernet(key) if key else None

    @staticmethod
    def hash_master_password(password):
        """
        Hash master password using SHA-256.
        """
        return base64.urlsafe_b64encode(
            hashlib.sha256(password.encode()).digest()
        )

    def set_key(self, key):
        """
        Set encryption key and initialize cipher.
        """
        self.key = key
        self.cipher = Fernet(key)

    def encrypt(self, data):
        """
        Encrypt byte data.
        """
        return self.cipher.encrypt(data)

    def decrypt(self, data):
        """
        Decrypt byte data.
        """
        return self.cipher.decrypt(data)

class PasswordManager:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("VAULT — Secure Password Manager")
        self.window.geometry("860x520")
        self.window.configure(bg=BG)
        self.window.resizable(False, False)

        self.security = SecurityManager()
        self.passwords = {}

        if not os.path.exists("master.key"):
            self.setup_master_password()
        else:
            self.login()

    # ── Helpers ────────────────────────────────────────────────
    def _dialog(self, title, w, h):
        d = tk.Toplevel(self.window)
        d.title(title)
        d.geometry(f"{w}x{h}")
        d.configure(bg=BG)
        d.grab_set()
        d.resizable(False, False)
        return d

    def _label(self, parent, text, size=10, bold=False, color=TEXT, **kw):
        return tk.Label(parent, text=text, bg=parent["bg"], fg=color,
                        font=(FONT, size, "bold" if bold else "normal"), **kw)

    def _entry(self, parent, show=""):
        e = tk.Entry(parent, show=show, width=34, bg=CARD, fg=TEXT,
                     insertbackground=ACCENT, relief="flat",
                     font=(FONT, 10), bd=0, highlightthickness=1,
                     highlightbackground=BORDER, highlightcolor=ACCENT)
        e.pack(pady=(2, 8), ipady=6, padx=30)
        return e

    def _btn(self, parent, text, cmd, color=ACCENT, side=None, **kw):
        b = tk.Button(parent, text=text, command=cmd, bg=color, fg=BG,
                      font=(FONT, 9, "bold"), relief="flat", bd=0,
                      activebackground=TEXT, activeforeground=BG,
                      cursor="hand2", padx=14, pady=6, **kw)
        if side:
            b.pack(side=side, padx=4)
        else:
            b.pack(pady=8)
        return b

    # ── Auth ───────────────────────────────────────────────────
    def setup_master_password(self):
        d = self._dialog("Create Vault", 380, 280)
        self._label(d, "VAULT", 20, bold=True, color=ACCENT).pack(pady=(28, 0))
        self._label(d, "Create your master password", 9, color=MUTED).pack(pady=(2, 14))

        self._label(d, "PASSWORD", 8, color=MUTED).pack(anchor="w", padx=30)
        pwd1 = self._entry(d, show="•")
        self._label(d, "CONFIRM", 8, color=MUTED).pack(anchor="w", padx=30)
        pwd2 = self._entry(d, show="•")

        def create():
            if not pwd1.get() or pwd1.get() != pwd2.get():
                messagebox.showerror("Error", "Passwords don't match or are empty!")
                return
            key = self.security.hash_master_password(pwd1.get())
            with open("master.key", "wb") as f:
                f.write(key)
            self.security.set_key(key)
            self.save_data()
            d.destroy()
            self.create_ui()

        self._btn(d, "CREATE VAULT", create, color=ACCENT2)

    def login(self):
        d = self._dialog("Unlock Vault", 380, 230)
        self._label(d, "VAULT", 20, bold=True, color=ACCENT).pack(pady=(28, 0))
        self._label(d, "Enter master password to unlock", 9, color=MUTED).pack(pady=(2, 16))

        self._label(d, "PASSWORD", 8, color=MUTED).pack(anchor="w", padx=30)
        pwd = self._entry(d, show="•")

        def verify():
            key = self.security.hash_master_password(pwd.get())
            with open("master.key", "rb") as f:
                if key != f.read():
                    messagebox.showerror("Error", "Incorrect password.")
                    return
            self.security.set_key(key)
            self.load_data()
            d.destroy()
            self.create_ui()

        pwd.bind("<Return>", lambda e: verify())
        self._btn(d, "UNLOCK", verify, color=ACCENT)

    # ── Data ───────────────────────────────────────────────────
    def save_data(self):
        data = json.dumps(self.passwords).encode()
        with open("passwords.enc", "wb") as f:
            f.write(self.security.encrypt(data))

    def load_data(self):
        if os.path.exists("passwords.enc"):
            with open("passwords.enc", "rb") as f:
                self.passwords = json.loads(self.security.decrypt(f.read()).decode())

    def check_strength(self, pwd):
        score = sum([len(pwd) >= 8, len(pwd) >= 12,
                     bool(re.search(r'[a-z]', pwd)), bool(re.search(r'[A-Z]', pwd)),
                     bool(re.search(r'\d', pwd)), bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd))])
        if score <= 2: return "WEAK", DANGER
        if score <= 4: return "MEDIUM", WARNING
        return "STRONG", ACCENT2
    
    def generate_password(self, length=10):
        """Generate a strong random password."""
        import random
        import string

        chars = (
            string.ascii_letters +
            string.digits +
            "!@#$%^&*()"
        )

        password = "".join(random.choice(chars) for _ in range(length))
        return password

    # ── Main UI ────────────────────────────────────────────────
    def create_ui(self):
        for w in self.window.winfo_children():
            w.destroy()

        # Sidebar
        sidebar = tk.Frame(self.window, bg=SURFACE, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Frame(sidebar, bg=ACCENT, width=200, height=3).pack(fill=tk.X)
        self._label(sidebar, "VAULT", 16, bold=True, color=ACCENT).pack(pady=(24, 2))
        self._label(sidebar, "Password Manager", 8, color=MUTED).pack()

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill=tk.X, padx=16, pady=20)

        actions = [("＋  ADD",    self.add_password,    ACCENT2),
                   ("◎  VIEW",   self.view_password,   ACCENT),
                   ("✎  EDIT",   self.edit_password,   WARNING),
                   ("✕  DELETE", self.delete_password, DANGER)]

        for label, cmd, color in actions:
            b = tk.Button(sidebar, text=label, command=cmd, bg=SURFACE, fg=color,
                          font=(FONT, 10, "bold"), relief="flat", bd=0,
                          activebackground=CARD, activeforeground=color,
                          cursor="hand2", anchor="w", padx=20, pady=10)
            b.pack(fill=tk.X)

        # Count badge
        self.count_lbl = self._label(sidebar, "", 8, color=MUTED)
        self.count_lbl.pack(side=tk.BOTTOM, pady=20)

        # Main panel
        main = tk.Frame(self.window, bg=BG)
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Search bar
        search_frame = tk.Frame(main, bg=BG)
        search_frame.pack(fill=tk.X, padx=20, pady=(16, 8))
        self._label(search_frame, "🔍", 11, color=MUTED).pack(side=tk.LEFT, padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.refresh_list())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                bg=CARD, fg=TEXT, insertbackground=ACCENT,
                                relief="flat", font=(FONT, 10), bd=0,
                                highlightthickness=1, highlightbackground=BORDER,
                                highlightcolor=ACCENT)
        search_entry.pack(fill=tk.X, expand=True, ipady=6)

        # Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vault.Treeview", background=CARD, foreground=TEXT,
                        fieldbackground=CARD, rowheight=36, font=(FONT, 10),
                        borderwidth=0)
        style.configure("Vault.Treeview.Heading", background=SURFACE,
                        foreground=MUTED, font=(FONT, 8, "bold"), relief="flat")
        style.map("Vault.Treeview", background=[("selected", BORDER)],
                  foreground=[("selected", ACCENT)])

        tree_frame = tk.Frame(main, bg=BG)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))

        scroll = ttk.Scrollbar(tree_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame, columns=("Website", "Username", "Strength"),
                                  show="headings", yscrollcommand=scroll.set,
                                  style="Vault.Treeview")
        for col, w in [("Website", 260), ("Username", 220), ("Strength", 90)]:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.tree.yview)

        self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        q = getattr(self, "search_var", None)
        query = q.get().lower() if q else ""
        for site, data in self.passwords.items():
            if query and query not in site.lower() and query not in data.get("username","").lower():
                continue
            strength, _ = self.check_strength(data.get("password",""))
            self.tree.insert("", tk.END, values=(site, data.get("username","—"), strength))
        if hasattr(self, "count_lbl"):
            n = len(self.passwords)
            self.count_lbl.config(text=f"{n} credential{'s' if n!=1 else ''} stored")

    # ── CRUD dialogs ───────────────────────────────────────────
    def _form_dialog(self, title, w, h, labels, values=None):
        d = self._dialog(title, w, h)
        self._label(d, title, 11, bold=True, color=ACCENT).pack(pady=(20, 12))
        fields = []
        for i, lbl in enumerate(labels):
            self._label(d, lbl.upper(), 8, color=MUTED).pack(anchor="w", padx=30)
            val = (values or [""] * len(labels))[i]
            show = "•" if "PASS" in lbl.upper() else ""
            e = self._entry(d, show=show)
            if val:
                e.insert(0, val)
            fields.append(e)
        return d, fields

    def add_password(self):
        d, fields = self._form_dialog("Add Credential", 400, 420,
                                      ["Website", "Username", "Password", "Notes"])
        sl = self._label(d, "Strength: —", 9, bold=True, color=MUTED)
        sl.pack()

        def upd(*_):
            s, c = self.check_strength(fields[2].get())
            sl.config(text=f"Strength: {s}", fg=c)
        fields[2].bind("<KeyRelease>", upd)

        def save():
            site, user, pwd, notes = [f.get() for f in fields]
            if not site or not pwd:
                messagebox.showerror("Error", "Website and Password are required."); return
            self.passwords[site] = {"username": user, "password": pwd, "notes": notes}
            self.save_data(); self.refresh_list()
            messagebox.showinfo("Saved", f"Credential for {site} saved."); d.destroy()

        self._btn(d, "SAVE", save, color=ACCENT2)

    def view_password(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a credential first."); return
        site = self.tree.item(sel[0])["values"][0]
        data = self.passwords[site]

        d = self._dialog(f"View — {site}", 420, 320)
        self._label(d, site, 13, bold=True, color=ACCENT).pack(pady=(20, 4))
        tk.Frame(d, bg=ACCENT, height=2, width=360).pack(pady=(0, 14))

        rows = [("Website", site), ("Username", data.get("username","—")),
                ("Password", data["password"]), ("Notes", data.get("notes","—"))]

        for lbl, val in rows:
            row = tk.Frame(d, bg=BG)
            row.pack(fill=tk.X, padx=28, pady=3)
            self._label(row, f"{lbl}:", 9, color=MUTED, width=9, anchor="w").pack(side=tk.LEFT)
            if lbl == "Password":
                pv = tk.Label(row, text="••••••••", bg=BG, fg=TEXT, font=(FONT, 10))
                pv.pack(side=tk.LEFT)
                def toggle(l=pv, v=val): l.config(text=v if l["text"]=="••••••••" else "••••••••")
                def copy(v=val): d.clipboard_clear(); d.clipboard_append(v); messagebox.showinfo("Copied","Password copied!")
                tk.Button(row, text="show", command=toggle, bg=CARD, fg=MUTED, relief="flat",
                          font=(FONT, 8), cursor="hand2", padx=6).pack(side=tk.LEFT, padx=4)
                tk.Button(row, text="copy", command=copy, bg=ACCENT, fg=BG, relief="flat",
                          font=(FONT, 8, "bold"), cursor="hand2", padx=6).pack(side=tk.LEFT)
            else:
                self._label(row, val, 10, color=TEXT, anchor="w").pack(side=tk.LEFT)

        self._btn(d, "CLOSE", d.destroy, color=BORDER)

    def edit_password(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a credential first."); return
        site = self.tree.item(sel[0])["values"][0]
        data = self.passwords[site]

        d, fields = self._form_dialog(f"Edit — {site}", 400, 380,
                                      ["Username", "Password", "Notes"],
                                      [data.get("username",""), data["password"], data.get("notes","")])
        sl = self._label(d, "", 9, bold=True)
        sl.pack()

        def upd(*_):
            s, c = self.check_strength(fields[1].get())
            sl.config(text=f"Strength: {s}", fg=c)
        fields[1].bind("<KeyRelease>", upd); upd()

        def save():
            user, pwd, notes = [f.get() for f in fields]
            if not pwd:
                messagebox.showerror("Error", "Password required."); return
            self.passwords[site] = {"username": user, "password": pwd, "notes": notes}
            self.save_data(); self.refresh_list()
            messagebox.showinfo("Updated", "Credential updated."); d.destroy()

        self._btn(d, "UPDATE", save, color=WARNING)

    def delete_password(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a credential first."); return
        site = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete", f"Permanently delete '{site}'?"):
            del self.passwords[site]
            self.save_data(); self.refresh_list()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PasswordManager()
    app.run()