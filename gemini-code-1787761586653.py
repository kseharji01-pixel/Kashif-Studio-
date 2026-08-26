import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import shutil
import json
from datetime import datetime

APP_NAME = "KASHIF STUDIO EZP"
APP_DIR = Path.home() / "KashifStudioEZP"
SETTINGS_FILE = APP_DIR / "settings.json"

DEFAULT_SETTINGS = {"studio_name": "KASHIF STUDIO"}

BG = "#070a0f"
CARD = "#111724"
CARD2 = "#0d1320"
BORDER = "#07566a"
TEXT = "#e8f0ff"
MUTED = "#8ca2c0"
CYAN = "#00d7ee"
GREEN = "#00d46a"
RED = "#ff4d4d"
PURPLE = "#b86cff"

def load_settings():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    save_settings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS.copy()

def save_settings(data):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

def unique_path(path):
    if not path.exists():
        return path
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return path.with_name(f"{path.stem}_{stamp}{path.suffix}")

class KashifStudioEZP(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.project = None
        self.media_files = []
        self.missing_files = []

        self.configure(bg=BG)
        self.title(f"{APP_NAME} — Licensed to: {self.settings['studio_name']}")
        self.geometry("1240x820")
        self.minsize(1000, 700)

        self._setup_style()
        self._build_ui()
        self.log(f"{APP_NAME} v1.0 initialized.")
        self.log("Ready to scan and consolidate EDIUS projects.")

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "TProgressbar",
            troughcolor=CARD2,
            background=CYAN,
            bordercolor=BORDER,
            lightcolor=CYAN,
            darkcolor=CYAN
        )

    def _card(self, parent):
        return tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1, bd=0)

    def _button(self, parent, text, command, accent=CYAN, width=16):
        return tk.Button(
            parent, text=text, command=command, width=width,
            bg=CARD2, fg=TEXT, activebackground=accent,
            activeforeground=BG, relief="flat", bd=0,
            highlightbackground=BORDER, highlightthickness=1,
            font=("Segoe UI", 9, "bold"), padx=8, pady=8,
            cursor="hand2"
        )

    def _build_ui(self):
        header = self._card(self)
        header.pack(fill="x", padx=16, pady=(16, 10))
        left = tk.Frame(header, bg=CARD)
        left.pack(side="left", padx=18, pady=14)
        tk.Label(left, text="KASHIF STUDIO EZP", bg=CARD, fg=CYAN, font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(left, text="EDIUS PROJECT EXTRACTOR • CONSOLIDATE • RELINK • VERIFY", bg=CARD, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(4, 0))

        head_btns = tk.Frame(header, bg=CARD)
        head_btns.pack(side="right", padx=18, pady=14)
        self._button(head_btns, "SETTINGS", self.open_settings, width=10).pack(side="left", padx=4)
        self._button(head_btns, "ABOUT", self.show_about, width=8).pack(side="left", padx=4)

        stats = tk.Frame(self, bg=BG)
        stats.pack(fill="x", padx=16, pady=(0, 10))
        self.stat_labels = {}
        for key, title, color in [
            ("projects", "PROJECTS", CYAN),
            ("references", "REFERENCES", TEXT),
            ("found", "FOUND", GREEN),
            ("missing", "MISSING", RED),
            ("quick", "QUICKTITLER", PURPLE),
            ("size", "TOTAL SIZE", CYAN),
        ]:
            card = self._card(stats)
            card.pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(card, text=title, bg=CARD, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(12, 2))
            lab = tk.Label(card, text="00" if key == "projects" else ("0.00 B" if key == "size" else "0"), bg=CARD, fg=color, font=("Segoe UI", 16, "bold"))
            lab.pack(anchor="w", padx=12, pady=(0, 12))
            self.stat_labels[key] = lab

        main = self._card(self)
        main.pack(fill="both", expand=True, padx=16, pady=(8, 10))

        drop = tk.Frame(main, bg=CARD2, highlightbackground=BORDER, highlightthickness=2, bd=0)
        drop.pack(fill="x", padx=12, pady=(12, 8))
        tk.Label(drop, text="DRAG & DROP EDIUS PROJECT (.EZP) HERE", bg=CARD2, fg=CYAN, font=("Segoe UI", 10, "bold")).pack(pady=(12, 2))
        self._button(drop, "OPEN EDIUS PROJECT", self.select_project, CYAN, 20).pack(pady=(6, 12))

        project_box = tk.Frame(main, bg=CARD2, highlightbackground=BORDER, highlightthickness=1)
        project_box.pack(fill="x", padx=12, pady=2)
        self.project_label = tk.Label(project_box, text="No project loaded", bg=CARD2, fg=TEXT, anchor="w", font=("Segoe UI", 9, "bold"))
        self.project_label.pack(fill="x", padx=12, pady=(9, 2))
        self.project_sub = tk.Label(project_box, text="Select an EDIUS .ezp file to begin extraction", bg=CARD2, fg=MUTED, anchor="w", font=("Segoe UI", 8))
        self.project_sub.pack(fill="x", padx=12, pady=(0, 9))

        loc = tk.Frame(main, bg=CARD2, highlightbackground=BORDER, highlightthickness=1)
        loc.pack(fill="x", padx=12, pady=8)
        tk.Label(loc, text="📁 SAVE LOCATION", bg=CARD2, fg=CYAN, font=("Segoe UI", 8, "bold")).pack(side="left", padx=12)
        self.save_var = tk.StringVar(value=str(Path.home() / "KashifStudioEZP_Output"))
        tk.Entry(loc, textvariable=self.save_var, bg="#09101a", fg=TEXT, insertbackground=TEXT, relief="flat", highlightbackground=BORDER, highlightthickness=1).pack(side="left", fill="x", expand=True, padx=4, pady=8)
        self._button(loc, "CHANGE FOLDER...", self.change_folder, CYAN, 15).pack(side="left", padx=4)
        self._button(loc, "OPEN FOLDER", self.open_folder, CYAN, 12).pack(side="left", padx=(0, 8))

        table_frame = tk.Frame(main, bg=CARD2, highlightbackground=BORDER, highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=12, pady=(2, 8))
        columns = ("category", "filename", "path", "size", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=7)
        headings = {"category": "CATEGORY", "filename": "FILENAME", "path": "ORIGINAL PATH", "size": "SIZE", "status": "STATUS"}
        widths = {"category": 110, "filename": 250, "path": 500, "size": 90, "status": 90}
        for c in columns:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        actions = tk.Frame(main, bg=CARD)
        actions.pack(fill="x", padx=12, pady=(0, 10))
        self._button(actions, "▶ CONSOLIDATE & SORT", self.consolidate, CYAN, 25).pack(side="left", padx=(0, 8))
        self._button(actions, "ADD MEDIA FILES", self.add_media, CYAN, 18).pack(side="left", padx=4)
        self._button(actions, "RESET UI", self.reset_all, CYAN, 12).pack(side="right")

        progress_card = self._card(self)
        progress_card.pack(fill="x", padx=16, pady=(0, 10))
        self.progress = ttk.Progressbar(progress_card, mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=12, pady=(10, 2))
        self.status = tk.StringVar(value="Ready")
        ttk.Label(progress_card, textvariable=self.status, background=CARD, foreground=MUTED, anchor="w").pack(fill="x", padx=12, pady=(0, 10))

        console_card = self._card(self)
        console_card.pack(fill="both", padx=16, pady=(0, 8))
        self.console = tk.Text(console_card, height=6, bg="#05080d", fg="#00d7ee", insertbackground=CYAN, relief="flat", font=("Consolas", 8))
        self.console.pack(fill="both", expand=True, padx=12, pady=(8, 8))
        self.console.configure(state="disabled")

    def log(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", f"[{datetime.now():%H:%M:%S}] {text}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def set_progress(self, value, message="Ready"):
        self.progress["value"] = value
        self.status.set(message)
        self.update_idletasks()

    def require_project(self):
        if not self.project:
            messagebox.showwarning(APP_NAME, "Please select an EDIUS/EZP project first.")
            return False
        return True

    def select_project(self):
        name = filedialog.askopenfilename(title="Select EDIUS Project", filetypes=[("EDIUS Project", "*.ezp *.ezp2 *.ezp3"), ("All files", "*.*")])
        if name:
            self.project = Path(name)
            self.project_label.config(text=self.project.name)
            self.project_sub.config(text=str(self.project))
            self.stat_labels["projects"].config(text="01")
            self.log(f"Project selected: {self.project}")

    def add_media(self):
        files = filedialog.askopenfilenames(title="Select Media Files")
        for item in files:
            if item not in self.media_files:
                self.media_files.append(item)
        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        total = 0
        for path_str in self.media_files:
            p = Path(path_str)
            exists = p.exists()
            size = p.stat().st_size if exists else 0
            total += size
            category = self._category(p)
            self.tree.insert("", "end", values=(category, p.name, str(p), self._human_size(size) if exists else "—", "FOUND" if exists else "MISSING"))
        self.stat_labels["references"].config(text=str(len(self.media_files)))
        self.stat_labels["found"].config(text=str(sum(Path(x).exists() for x in self.media_files)))
        self.stat_labels["missing"].config(text=str(sum(not Path(x).exists() for x in self.media_files)))
        self.stat_labels["size"].config(text=self._human_size(total))

    def _category(self, p):
        ext = p.suffix.lower()
        if ext in {".mp4", ".mov", ".avi", ".mxf", ".mts", ".m2ts", ".mkv", ".wmv"}: return "VIDEO"
        if ext in {".wav", ".mp3", ".aac", ".flac", ".m4a"}: return "AUDIO"
        if ext in {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}: return "IMAGE"
        if ext in {".psd", ".ai", ".eps", ".svg", ".txt", ".rtf", ".etl"}: return "GRAPHICS"
        return "OTHER"

    def _human_size(self, n):
        units = ["B","KB","MB","GB","TB"]
        n = float(n)
        for u in units:
            if n < 1024 or u == units[-1]:
                return f"{n:.2f} {u}"
            n /= 1024

    def change_folder(self):
        folder = filedialog.askdirectory(title="Select Save Location")
        if folder: self.save_var.set(folder)

    def open_folder(self):
        p = Path(self.save_var.get())
        p.mkdir(parents=True, exist_ok=True)
        import os
        os.startfile(str(p))

    def consolidate(self):
        if not self.require_project(): return
        
        root = Path(self.save_var.get()) / f"{self.project.stem}_Consolidated"
        folders = {
            "VIDEO": root / "Videos",
            "AUDIO": root / "Audio",
            "IMAGE": root / "Images",
            "GRAPHICS": root / "Graphics_and_Text",
            "OTHER": root / "Other_Files"
        }
        
        for folder in folders.values():
            folder.mkdir(parents=True, exist_ok=True)
            
        shutil.copy2(self.project, root / self.project.name)
        
        copied = 0
        for item in self.media_files:
            src = Path(item)
            if src.exists():
                category = self._category(src)
                dest_folder = folders.get(category, folders["OTHER"])
                shutil.copy2(src, unique_path(dest_folder / src.name))
                copied += 1
                
        self.log(f"Consolidation completed: {copied} file(s) sorted into subfolders.")
        self.set_progress(100, f"Consolidated & Sorted {copied} file(s) successfully ✓")
        messagebox.showinfo(APP_NAME, f"All files successfully organized into separate folders:\n{root}")

    def reset_all(self):
        self.project = None
        self.media_files.clear()
        self.project_label.config(text="No project loaded")
        self.stat_labels["projects"].config(text="00")
        self.progress["value"] = 0
        self.refresh_table()
        self.status.set("Ready")

    def open_settings(self):
        win = tk.Toplevel(self)
        win.title("Settings")
        win.geometry("400x150")
        win.configure(bg=BG)
        tk.Label(win, text="Studio Name", bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(pady=10)
        var = tk.StringVar(value=self.settings["studio_name"])
        entry = tk.Entry(win, textvariable=var, bg=CARD2, fg=TEXT, width=30)
        entry.pack(pady=5)
        def save():
            self.settings["studio_name"] = var.get().strip() or "KASHIF STUDIO"
            save_settings(self.settings)
            self.title(f"{APP_NAME} — Licensed to: {self.settings['studio_name']}")
            win.destroy()
        self._button(win, "SAVE", save, CYAN, 12).pack(pady=10)

    def show_about(self):
        messagebox.showinfo("About", f"{APP_NAME}\n\nLicensed to: {self.settings['studio_name']}")

if __name__ == "__main__":
    app = KashifStudioEZP()
    app.mainloop()