import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from asammdf import MDF
from src.cantransform import *
import cantools
import os
from datetime import datetime, time
from zoneinfo import ZoneInfo
from tkcalendar import DateEntry

class MF4ExporterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MF4 zu CSV Exporter")
        self.geometry("950x700")

        self.dbc = None
        self.dbc_file = None
        self.mf4_paths = []
        self.available_signals = []

        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        # DBC
        ttk.Label(frm, text="DBC-Datei:").grid(row=0, column=0, sticky="w")
        self.dbc_entry = ttk.Entry(frm, width=75)
        self.dbc_entry.grid(row=0, column=1, sticky="w")
        ttk.Button(frm, text="Auswählen", command=self.select_dbc).grid(row=0, column=2)

        # MF4 single
        ttk.Label(frm, text="MF4-Datei:").grid(row=1, column=0, sticky="w")
        self.mf4_entry = ttk.Entry(frm, width=75)
        self.mf4_entry.grid(row=1, column=1, sticky="w")
        ttk.Button(frm, text="Datei wählen", command=self.select_mf4_file).grid(row=1, column=2)

        # MF4 folder
        ttk.Label(frm, text="oder Ordner:").grid(row=2, column=0, sticky="w")
        self.folder_entry = ttk.Entry(frm, width=75)
        self.folder_entry.grid(row=2, column=1, sticky="w")
        ttk.Button(frm, text="Ordner wählen", command=self.select_folder).grid(row=2, column=2)

        # Time range (CET) with DateTimePicker
        ttk.Label(frm, text="Von (CET):").grid(row=3, column=0, sticky="w")
        self.from_date = DateEntry(frm, width=12, date_pattern="yyyy-mm-dd")
        self.from_date.grid(row=3, column=1, sticky="w")
        self.from_hour = ttk.Spinbox(frm, from_=0, to=23, width=3, format="%02.0f")
        self.from_hour.grid(row=3, column=1, sticky="e", padx=(0, 110))
        self.from_min = ttk.Spinbox(frm, from_=0, to=59, width=3, format="%02.0f")
        self.from_min.grid(row=3, column=1, sticky="e", padx=(0, 75))
        self.from_sec = ttk.Spinbox(frm, from_=0, to=59, width=3, format="%02.0f")
        self.from_sec.grid(row=3, column=1, sticky="e", padx=(0, 40))

        ttk.Label(frm, text="Bis (CET):").grid(row=4, column=0, sticky="w")
        self.to_date = DateEntry(frm, width=12, date_pattern="yyyy-mm-dd")
        self.to_date.grid(row=4, column=1, sticky="w")
        self.to_hour = ttk.Spinbox(frm, from_=0, to=23, width=3, format="%02.0f")
        self.to_hour.grid(row=4, column=1, sticky="e", padx=(0, 110))
        self.to_min = ttk.Spinbox(frm, from_=0, to=59, width=3, format="%02.0f")
        self.to_min.grid(row=4, column=1, sticky="e", padx=(0, 75))
        self.to_sec = ttk.Spinbox(frm, from_=0, to=59, width=3, format="%02.0f")
        self.to_sec.grid(row=4, column=1, sticky="e", padx=(0, 40))

        # Load signals
        ttk.Button(frm, text="Signale laden", command=self.load_signals).grid(row=5, column=0, pady=5)

        # Signal list
        self.signal_listbox = tk.Listbox(frm, selectmode=tk.MULTIPLE, width=90, height=15)
        self.signal_listbox.grid(row=6, column=0, columnspan=3, sticky="w")

        # Export
        ttk.Button(frm, text="CSV exportieren", command=self.export_csv).grid(row=7, column=0, pady=10)

    def select_dbc(self):
        path = filedialog.askopenfilename(filetypes=[("DBC files", "*.dbc")])
        if path:
            self.dbc_entry.delete(0, tk.END)
            self.dbc_entry.insert(0, path)
            self.dbc = cantools.database.load_file(path)
            self.dbc_file = path

    def select_mf4_file(self):
        path = filedialog.askopenfilename(filetypes=[("MF4 files", "*.mf4")])
        if path:
            self.mf4_entry.delete(0, tk.END)
            self.mf4_entry.insert(0, path)
            self.folder_entry.delete(0, tk.END)
            self.mf4_paths = [path]

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, path)
            self.mf4_entry.delete(0, tk.END)
            self.mf4_paths = [
                os.path.join(root, f)
                for root, _, files in os.walk(path)
                for f in files
                if f.lower().endswith(".mf4")
            ]
            messagebox.showinfo("MF4-Dateien", f"{len(self.mf4_paths)} MF4-Dateien gefunden (rekursiv).")

    def load_signals(self):
        if not self.mf4_paths:
            messagebox.showerror("Fehler", "Bitte MF4-Datei oder Ordner wählen")
            return

        mdf = MDF(self.mf4_paths[0])
        decoded_mdf = decode_file(self.mf4_paths[0], self.dbc)
        self.available_signals = list(decoded_mdf.channels_db.keys())
        self.signal_listbox.delete(0, tk.END)
        for sig in sorted(self.available_signals):
            self.signal_listbox.insert(tk.END, sig)

        # Default time range = whole file
        start = decoded_mdf.start_time
        if start.tzinfo is None:
            start = start.replace(tzinfo=ZoneInfo("UTC"))
        start_cet = start.astimezone(ZoneInfo("Europe/Berlin"))

        self.from_date.set_date(start_cet.date())
        self.from_hour.set(start_cet.strftime("%H"))
        self.from_min.set(start_cet.strftime("%M"))
        self.from_sec.set(start_cet.strftime("%S"))

    def _get_cet_datetime(self, date_entry, h_spin, m_spin, s_spin):
        try:
            d = date_entry.get_date()
            t = time(int(h_spin.get()), int(m_spin.get()), int(s_spin.get()))
            dt = datetime.combine(d, t)
            return dt.replace(tzinfo=ZoneInfo("Europe/Berlin"))
        except Exception:
            raise ValueError("Ungültige Datum/Uhrzeit-Eingabe")

    def export_csv(self):
        selected = [self.signal_listbox.get(i) for i in self.signal_listbox.curselection()]
        if not selected:
            messagebox.showerror("Fehler", "Bitte mindestens ein Signal wählen")
            return

        out_dir = filedialog.askdirectory(title="Zielordner wählen")
        if not out_dir:
            return

        try:
            from_dt = self._get_cet_datetime(self.from_date, self.from_hour, self.from_min, self.from_sec)
            to_dt = self._get_cet_datetime(self.to_date, self.to_hour, self.to_min, self.to_sec)
        except ValueError as e:
            messagebox.showerror("Fehler", str(e))
            return

        if from_dt >= to_dt:
            messagebox.showerror("Fehler", "'Von' muss vor 'Bis' liegen")
            return

        for mf4 in self.mf4_paths:
            mdf = MDF(mf4)

            start_time = mdf.start_time
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=ZoneInfo("UTC"))

            t_from = (from_dt.astimezone(start_time.tzinfo) - start_time).total_seconds()
            t_to = (to_dt.astimezone(start_time.tzinfo) - start_time).total_seconds()

            mdf_cut = mdf.cut(start=t_from, stop=t_to)

            df = mdf_cut.to_dataframe(channels=selected)
            base = os.path.splitext(os.path.basename(mf4))[0]
            out_path = os.path.join(out_dir, base + ".csv")
            df.to_csv(out_path, index=False)

        messagebox.showinfo("Fertig", "CSV Export abgeschlossen")


if __name__ == "__main__":
    app = MF4ExporterApp()
    app.mainloop()
