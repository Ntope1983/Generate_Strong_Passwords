import math
import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox

AMBIGUOUS = "Il1O0o"
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?/"


def build_pools(use_lower, use_upper, use_digits, use_symbols, no_ambiguous):
    pools = []
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append(SYMBOLS)
    if no_ambiguous:
        pools = ["".join(c for c in p if c not in AMBIGUOUS) for p in pools]
    return [p for p in pools if p]


def generate_password(length, pools):
    """Δημιουργεί κωδικό με το secrets (κρυπτογραφικά ασφαλές),
    εγγυώμενο τουλάχιστον έναν χαρακτήρα από κάθε επιλεγμένη κατηγορία."""
    all_chars = "".join(pools)
    chars = [secrets.choice(p) for p in pools]
    chars += [secrets.choice(all_chars) for _ in range(length - len(chars))]
    # ανακάτεμα με ασφαλή τυχαιότητα
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def strength(length, pool_size):
    bits = length * math.log2(pool_size) if pool_size > 1 else 0
    if bits < 40:
        return "Πολύ αδύναμος", "#d32f2f", bits
    if bits < 60:
        return "Αδύναμος", "#f57c00", bits
    if bits < 80:
        return "Καλός", "#fbc02d", bits
    if bits < 110:
        return "Ισχυρός", "#388e3c", bits
    return "Πολύ ισχυρός", "#1b5e20", bits


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Γεννήτρια Ισχυρών Κωδικών")
        self.geometry("520x470")
        self.resizable(False, False)

        self.length_var = tk.IntVar(value=16)
        self.lower_var = tk.BooleanVar(value=True)
        self.upper_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.ambig_var = tk.BooleanVar(value=False)
        self.password_var = tk.StringVar()
        self.show_var = tk.BooleanVar(value=True)

        self._build_ui()
        self.generate()

    def _build_ui(self):
        pad = {"padx": 15, "pady": 6}

        ttk.Label(self, text="Γεννήτρια Ισχυρών Κωδικών",
                  font=("Segoe UI", 15, "bold")).pack(pady=(15, 5))

        # Μήκος
        frame_len = ttk.LabelFrame(self, text="Μήκος κωδικού")
        frame_len.pack(fill="x", **pad)
        self.len_label = ttk.Label(frame_len, text="16", width=4,
                                   font=("Segoe UI", 11, "bold"))
        self.len_label.pack(side="right", padx=10)
        ttk.Scale(frame_len, from_=8, to=64, orient="horizontal",
                  command=self._on_scale).pack(side="left", fill="x",
                                               expand=True, padx=10, pady=8)
        self.scale = frame_len.winfo_children()[-1]
        self.scale.set(16)

        # Επιλογές
        frame_opt = ttk.LabelFrame(self, text="Χαρακτήρες")
        frame_opt.pack(fill="x", **pad)
        opts = [
            ("Πεζά (a-z)", self.lower_var),
            ("Κεφαλαία (A-Z)", self.upper_var),
            ("Αριθμοί (0-9)", self.digits_var),
            ("Σύμβολα (!@#$...)", self.symbols_var),
            ("Αποφυγή παρόμοιων χαρακτήρων (I, l, 1, O, 0, o)", self.ambig_var),
        ]
        for text, var in opts:
            ttk.Checkbutton(frame_opt, text=text, variable=var,
                            command=self.generate).pack(anchor="w", padx=10, pady=2)

        # Αποτέλεσμα
        frame_out = ttk.LabelFrame(self, text="Κωδικός")
        frame_out.pack(fill="x", **pad)
        self.entry = ttk.Entry(frame_out, textvariable=self.password_var,
                               font=("Consolas", 13), justify="center")
        self.entry.pack(fill="x", padx=10, pady=(10, 5))
        ttk.Checkbutton(frame_out, text="Εμφάνιση κωδικού",
                        variable=self.show_var,
                        command=self._toggle_show).pack(anchor="w", padx=10)

        self.strength_label = ttk.Label(frame_out, text="",
                                        font=("Segoe UI", 10, "bold"))
        self.strength_label.pack(pady=(5, 8))

        # Κουμπιά
        frame_btn = ttk.Frame(self)
        frame_btn.pack(pady=8)
        ttk.Button(frame_btn, text="Δημιουργία νέου",
                   command=self.generate, width=18).pack(side="left", padx=5)
        ttk.Button(frame_btn, text="Αντιγραφή",
                   command=self.copy, width=18).pack(side="left", padx=5)

    def _on_scale(self, value):
        self.length_var.set(int(float(value)))
        self.len_label.config(text=str(self.length_var.get()))
        if hasattr(self, "entry"):
            self.generate()

    def _toggle_show(self):
        self.entry.config(show="" if self.show_var.get() else "•")

    def generate(self):
        pools = build_pools(self.lower_var.get(), self.upper_var.get(),
                            self.digits_var.get(), self.symbols_var.get(),
                            self.ambig_var.get())
        if not pools:
            self.password_var.set("")
            self.strength_label.config(text="Επίλεξε τουλάχιστον μία κατηγορία",
                                       foreground="#d32f2f")
            return
        length = max(self.length_var.get(), len(pools))
        pwd = generate_password(length, pools)
        self.password_var.set(pwd)
        label, color, bits = strength(length, len("".join(pools)))
        self.strength_label.config(
            text=f"Ισχύς: {label} (~{int(bits)} bits)", foreground=color)

    def copy(self):
        pwd = self.password_var.get()
        if not pwd:
            messagebox.showwarning("Προσοχή", "Δεν υπάρχει κωδικός για αντιγραφή.")
            return
        self.clipboard_clear()
        self.clipboard_append(pwd)
        self.update()
        self.strength_label.config(text="Αντιγράφηκε στο πρόχειρο ✔",
                                   foreground="#1b5e20")
        # καθαρισμός του πρόχειρου μετά από 30 δευτερόλεπτα
        self.after(30000, self._clear_clipboard)

    def _clear_clipboard(self):
        try:
            self.clipboard_clear()
        except tk.TclError:
            pass


if __name__ == "__main__":
    App().mainloop()