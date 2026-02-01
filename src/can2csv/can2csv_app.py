import json
import tkinter as tk
from enum import Enum
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter import ttk
from can2csv.cantransform import *
import cantools
import os
from datetime import datetime

DT_FORMAT = "%Y-%m-%d %H:%M"

CONFIG_FILE = Path.home() / ".can2csv_config.json"


class ChoiceType(Enum):
    LAST_DBC = "last_dbc_file"
    LAST_DBC_DIR = "last_output_file"
    LAST_MDF_DIR = "last_mdf_dir"
    LAST_OUTPUT_DIR = "last_output_file"


class Can2CsvApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("MF4 zu CSV Exporter")
        self.geometry("950x700")

        self.last_paths = {}
        self.dbc = None
        self.dbc_file = None
        self.mf4_paths = []
        self.available_signals = []
        # self.decoded_mdfs = []
        self.mdf_min_time = None
        self.mdf_max_time = None
        self.out_dir = None
        self.mf4_folder_entry = None
        self.from_entry = None
        self.to_entry = None
        self.timegrid_var = tk.StringVar(value="0.01")  # Default: 10 ms


        self._build_ui()

    def _build_ui(self):
        self.load_last_paths()
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        # DBC
        ttk.Label(frm, text="DBC-Datei:").grid(row=0, column=0, sticky="w")
        self.dbc_entry = ttk.Entry(frm, width=75)
        self.dbc_entry.grid(row=0, column=1, sticky="w")
        if self.last_paths and self.last_paths[ChoiceType.LAST_DBC.value]:
            self.dbc_entry.insert(0, self.last_paths[ChoiceType.LAST_DBC.value])
            self.dbc_file = self.last_paths[ChoiceType.LAST_DBC.value]
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

        # Show Graphic
        # ttk.Button(frm, text="Daten anzeigen", command=self.show_plot_custom_data).grid(row=5, column=0, pady=5)

        # Load signals
        # ttk.Button(frm, text="Signale laden", command=self.load_signals).grid(row=5, column=0, pady=5)

        # # Signal list
        # self.signal_listbox = tk.Listbox(frm, selectmode=tk.MULTIPLE, width=90, height=15)
        # self.signal_listbox.grid(row=8, column=0, columnspan=3, sticky="w")

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
        if self.out_dir:
            self.csv_folder_entry.insert(0, self.out_dir)
        ttk.Button(frm, text="Ordner wählen", command=self.select_csv_folder).grid(row=12, column=2)

        # Export-Dateiname
        ttk.Label(frm, text="Export-Dateiname").grid(row=13, column=0, sticky="w")
        self.csv_filename_entry = ttk.Entry(frm, width=75)
        self.csv_filename_entry.grid(row=13, column=1, sticky="w")
        self.csv_filename_entry.insert(0, "output.csv")

        # ttk.Label(frm, text="Zeitraster [s]:").grid(row=14, column=0, sticky="w")
        # ttk.Entry(frm, textvariable=self.timegrid_var, width=10).grid(row=14, column=1, sticky="w")

        # Export-Button
        ttk.Button(frm, text="CSV exportieren", command=self.export_csv).grid(row=16, column=0, pady=10)

    def safe_path(self, str_path: str):
        result = Path.home()
        if str_path:
            result_path = Path(str_path)
            if result_path:
                result = str(result_path)
        return result

    def select_dbc(self):
        initpath =  self.safe_path(self.last_paths.get(ChoiceType.LAST_DBC_DIR.value))
        path = filedialog.askopenfilename(
            filetypes=[("DBC files", "*.dbc")],
            title = "DBC-Datei wählen",
            initialdir = initpath
        )
        if path:
            self.dbc_entry.delete(0, tk.END)
            self.dbc_entry.insert(0, path)
            self.dbc = cantools.database.load_file(path)
            self.dbc_file = path
            self.save_last_choice(ChoiceType.LAST_DBC, path)
            self.save_last_choice(ChoiceType.LAST_DBC_DIR, os.path.basename(path))

    def select_mf4_file(self):
        path = filedialog.askopenfilename(filetypes=[("MF4 files", "*.mf4")])
        if path:
            self.mf4_entry.delete(0, tk.END)
            self.mf4_entry.insert(0, path)
            self.mf4_folder_entry.delete(0, tk.END)
            self.mf4_paths = [path]

    def select_mf4_folder(self):
        initpath = self.safe_path(self.last_paths.get(ChoiceType.LAST_MDF_DIR.value))
        path = filedialog.askdirectory(
            title="MDF-Verzeichnis wählen",
            initialdir=initpath
        )
        self.update_mf4_folder_entry(path)
        messagebox.showinfo("MF4-Dateien", f"{len(self.mf4_paths)} MF4-Dateien gefunden (rekursiv).")

    def update_mf4_folder_entry(self, path):
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
            self.save_last_choice(ChoiceType.LAST_MDF_DIR, path)

    def select_csv_folder(self):
        initpath = self.safe_path(self.last_paths.get(ChoiceType.LAST_OUTPUT_DIR.value))
        path = filedialog.askdirectory(
            title="Ausgabeverzeichnis wählen",
            initialdir=initpath
        )
        if path:
            self.csv_folder_entry.delete(0, tk.END)
            self.csv_folder_entry.insert(0, path)
            self.out_dir = path
            self.save_last_choice(ChoiceType.LAST_OUTPUT_DIR, path)

    def load_signals(self):
        if not self.mf4_paths:
            messagebox.showerror("Fehler", "Bitte MF4-Datei oder Ordner wählen")
            return

        decoded_mdf = decode_file(self.mf4_paths[0], self.dbc_file)
        self.available_signals = get_available_signals(decoded_mdf)
        # self.signal_listbox.delete(0, tk.END)
        # for sig in sorted(self.available_signals):
        #     self.signal_listbox.insert(tk.END, sig)
        #
        # # Default time range = whole file
        # start = decoded_mdf.start_time
        # if start.tzinfo is None:
        #     start = start.replace(tzinfo=ZoneInfo("UTC"))
        # start_cet = start.astimezone(ZoneInfo("Europe/Berlin"))

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
        if not self.mf4_paths:
            messagebox.showerror("Fehler", "Keine MF4-Dateien gefunden")
            return
        decoded_mdf = decode_file(self.mf4_paths[0], self.dbc_file)
        self.available_signals = get_available_signals(decoded_mdf)
        signals_selected = self.available_signals

        if not signals_selected:
            messagebox.showerror("Fehler", "Keine passenden Signale in mf4 gefunden")
            return

        if not self.out_dir:
            messagebox.showerror("Fehler", "Bitte einen Output-Ordner wählen")
            return

        out_filename = self.csv_filename_entry.get()

        if not out_filename:
            messagebox.showerror("Fehler", "Bitte Ausgabe-Dateinamen angeben")

        if not out_filename.endswith(".csv"):
            out_filename = out_filename + ".csv"

        out_path = os.path.join(self.out_dir, out_filename)
        decoded_files = [ decode_file(mdf, self.dbc_file) for mdf in self.mf4_paths]
        filenames = export_to_csv(out_path, decoded_files, signals_selected)

        msg = "CSV-Export abgeschlossen.\n"
        for file in filenames:
            msg += f"\t{file}\n"
        messagebox.showinfo("Fertig", msg)


    def show_plot_custom_data(self):
        if not self.mf4_paths:
            messagebox.showerror("Fehler", "Keine MF4-Dateien gefunden")
            return
        decoded_mdf = decode_file(self.mf4_paths[0], self.dbc_file)
        self.available_signals = get_available_signals(decoded_mdf)
        signals_selected = self.available_signals

        if not signals_selected:
            messagebox.showerror("Fehler", "Keine passenden Signale in mf4 gefunden")
            return

        decoded_files = [ decode_file(mdf, self.dbc_file) for mdf in self.mf4_paths]
        custom_data = calculate_custom_values(decoded_files)

        print_custom_data(custom_data)



    def save_last_choice(self, choice_type: ChoiceType, choice_path: str):
        if CONFIG_FILE.exists() and self.last_paths is None:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.last_paths = json.load(f)

        self.last_paths[choice_type.value] = choice_path

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.last_paths, f, indent=2)

    def get_timegrid_seconds(self) -> float:
        try:
            value = float(self.timegrid_var.get())
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            messagebox.showinfo("Fehler", "Zeitraster muss eine positive Zahl in Sekunden sein")

    def load_last_paths(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.last_paths = json.load(f)
            if self.last_paths:
                if self.last_paths[ChoiceType.LAST_DBC.value]:
                    self.dbc_file = ChoiceType.LAST_DBC.value
                if self.last_paths[ChoiceType.LAST_MDF_DIR.value]:
                    self.mf4_folder_entry = ChoiceType.LAST_MDF_DIR.value
                if self.last_paths[ChoiceType.LAST_OUTPUT_DIR.value]:
                    self.out_dir = self.last_paths[ChoiceType.LAST_OUTPUT_DIR.value]


if __name__ == "__main__":
    app = Can2CsvApp()
    app.mainloop()
