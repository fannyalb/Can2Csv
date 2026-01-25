import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from asammdf import MDF
from src.cantransform import *
import cantools
import os
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo
from tkcalendar import DateEntry

DT_FORMAT = "%Y-%m-%d %H:%M"

class MF4ExporterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MF4 zu CSV Exporter")
        self.geometry("950x700")

        self.dbc = None
        self.dbc_file = None
        self.mf4_paths = []
        self.available_signals = []
        # self.decoded_mdfs = []
        self.mdf_min_time = None
        self.mdf_max_time = None
        self.out_dir = None

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
        self.mf4_folder_entry = ttk.Entry(frm, width=75)
        self.mf4_folder_entry.grid(row=2, column=1, sticky="w")
        ttk.Button(frm, text="Ordner wählen", command=self.select_mf4_folder).grid(row=2, column=2)

        # Load signals
        ttk.Button(frm, text="Signale laden", command=self.load_signals).grid(row=5, column=0, pady=5)

        # Signal list
        self.signal_listbox = tk.Listbox(frm, selectmode=tk.MULTIPLE, width=90, height=15)
        self.signal_listbox.grid(row=8, column=0, columnspan=3, sticky="w")

        # # Time range as string fields
        # ttk.Label(frm, text=f"Von:").grid(row=6, column=0, sticky="w")
        # self.from_entry = ttk.Entry(frm, width=25)
        # self.from_entry.grid(row=6, column=1, sticky="w")
        #
        # ttk.Label(frm, text=f"Bis:").grid(row=7, column=0, sticky="w")
        # self.to_entry = ttk.Entry(frm, width=25)
        # self.to_entry.grid(row=7, column=1, sticky="w")

        # Export-Folder
        ttk.Label(frm, text="Export-Ordner").grid(row=12, column=0, sticky="w")
        self.csv_folder_entry = ttk.Entry(frm, width=75)
        self.csv_folder_entry.grid(row=12, column=1, sticky="w")
        ttk.Button(frm, text="Ordner wählen", command=self.select_csv_folder).grid(row=12, column=2)

        # Export-Dateiname
        ttk.Label(frm, text="Export-Dateiname").grid(row=13, column=0, sticky="w")
        self.csv_filename_entry = ttk.Entry(frm, width=75)
        self.csv_filename_entry.grid(row=13, column=1, sticky="w")
        self.csv_filename_entry.insert(0, "output.csv")

        # Export-Button
        ttk.Button(frm, text="CSV exportieren", command=self.export_csv).grid(row=15, column=0, pady=10)

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
            self.mf4_folder_entry.delete(0, tk.END)
            self.mf4_paths = [path]

    def select_mf4_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.mf4_folder_entry.delete(0, tk.END)
            self.mf4_folder_entry.insert(0, path)
            self.mf4_entry.delete(0, tk.END)
            self.mf4_paths = [
                os.path.join(root, f)
                for root, _, files in os.walk(path)
                for f in files
                if f.lower().endswith(".mf4")
            ]
            messagebox.showinfo("MF4-Dateien", f"{len(self.mf4_paths)} MF4-Dateien gefunden (rekursiv).")

    def select_csv_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.csv_folder_entry.delete(0, tk.END)
            self.csv_folder_entry.insert(0, path)
            self.out_dir = path

    def load_signals(self):
        if not self.mf4_paths:
            messagebox.showerror("Fehler", "Bitte MF4-Datei oder Ordner wählen")
            return

        decoded_mdf = decode_file(self.mf4_paths[0], self.dbc_file)
        self.available_signals = get_available_signals(decoded_mdf)
        self.signal_listbox.delete(0, tk.END)
        for sig in sorted(self.available_signals):
            self.signal_listbox.insert(tk.END, sig)

        # Default time range = whole file
        start = decoded_mdf.start_time
        if start.tzinfo is None:
            start = start.replace(tzinfo=ZoneInfo("UTC"))
        start_cet = start.astimezone(ZoneInfo("Europe/Berlin"))

        # self.find_min_max_datetime()
        # self.set_min_max_datetime()

    def find_min_max_datetime(self):
        if not self.mf4_paths:
            return

        min_time = None
        max_time = None
        for mdf in self.mf4_paths:
            start_time = to_cet(datetime.fromtimestamp(path.getmtime(mdf)))
            print(start_time)
            min_time = min(min_time, start_time) if min_time is not None else start_time
            max_time = max(max_time, start_time) if max_time is not None else start_time

        self.mdf_min_time, self.mdf_max_time = min_time, max_time

    def set_min_max_datetime(self):
        min_dt = datetime.strftime(self.mdf_min_time, DT_FORMAT)
        max_dt = datetime.strftime(self.mdf_max_time, DT_FORMAT)
        self.from_entry.delete(0, tk.END)
        self.from_entry.insert(0, min_dt)
        self.to_entry.delete(0, tk.END)
        self.to_entry.insert(0, max_dt)


    def export_csv(self):
        selected = [self.signal_listbox.get(i) for i in self.signal_listbox.curselection()]
        if not selected:
            messagebox.showerror("Fehler", "Bitte mindestens ein Signal wählen")
            return

        if not self.out_dir:
            messagebox.showerror("Fehler", "Bitte keinen Output-Ordner gewählt")
            return

        out_filename = self.csv_filename_entry.get()

        if not out_filename:
            messagebox.showerror("Fehler", "Bitte Ausgabe-Dateinamen angeben")

        if not out_filename.endswith(".csv"):
            out_filename = out_filename + ".csv"

        # try:
        #     from_dt = self._get_cet_datetime(self.from_date, self.from_hour, self.from_min, self.from_sec)
        #     to_dt = self._get_cet_datetime(self.to_date, self.to_hour, self.to_min, self.to_sec)
        # except ValueError as e:
        #     messagebox.showerror("Fehler", str(e))
        #     return

        # if from_dt >= to_dt:
        #     messagebox.showerror("Fehler", "'Von' muss vor 'Bis' liegen")
        #     return

        # for mf4 in self.mf4_paths:
        #     mdf = MDF(mf4)
        #
        #     start_time = mdf.start_time
        #     if start_time.tzinfo is None:
        #         start_time = start_time.replace(tzinfo=ZoneInfo("UTC"))
        #
        #     t_from = (from_dt.astimezone(start_time.tzinfo) - start_time).total_seconds()
        #     t_to = (to_dt.astimezone(start_time.tzinfo) - start_time).total_seconds()
        #
        #     mdf_cut = mdf.cut(start=t_from, stop=t_to)
        #
        #     df = mdf_cut.to_dataframe(channels=selected)
        #     base = os.path.splitext(os.path.basename(mf4))[0]
        #     out_path = os.path.join(out_dir, base + ".csv")
        #     df.to_csv(out_path, index=False)
        out_path = os.path.join(self.out_dir, out_filename)
        decoded_files = [ decode_file(mdf, self.dbc_file) for mdf in self.mf4_paths]
        filenames = export_to_csv(out_path, decoded_files, selected)

        messagebox.showinfo("Fertig", f'CSV Export nach {filenames[0]} abgeschlossen')


if __name__ == "__main__":
    app = MF4ExporterApp()
    app.mainloop()
