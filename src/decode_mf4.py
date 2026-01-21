from datetime import timedelta
import matplotlib.pyplot as plt
from os import path

import pandas as pd

from asammdf import MDF
import cantools
from pandas.core.interchange.dataframe_protocol import DataFrame

dbc_file = "../tests/data/beispiel1.dbc"
mymdf_file ="../tests/data/beispiel1.mf4"

def decode_file(mdf_file, dbc_file):
    if not path.isfile(mdf_file):
        print(f'{mdf_file} ist keine valide Datei')
    if not path.isfile(dbc_file):
        print(f'{dbc_file} ist keine valide Datei')

    dbs = {
        "CAN": [(dbc_file, 0)],
    }
    with MDF(mdf_file) as mdf:
        decoded = mdf.extract_bus_logging(database_files=dbs)

    return decoded

def get_single_channel_df(decoded_mdf: MDF, signal_name: str):
    signal = decoded_mdf.get(signal_name)
    values = signal.samples
    times = signal.timestamps
    time_start = decoded_mdf.start_time
    timestamps = [time_start + timedelta(seconds=t) for t in times]
    dataframe = pd.DataFrame({"Time": timestamps, signal_name: values})
    return dataframe

def get_signals_df(decoded_mdf: MDF, signal_names: list[str]):
#     signal = decoded_mdf.get(signal_name)
#     values = signal.samples
#     times = signal.timestamps
#     time_start = decoded_mdf.start_time
#     timestamps = [time_start + timedelta(seconds=t) for t in times]
#     dataframe = pd.DataFrame({"Time": timestamps, signal_name: values})
    dataframe = None
    return dataframe

def print_signal(signal_df):
    signal_name = signal_df.columns[1]
    title = f'{signal_name} over Time'
    signal_df.plot(x="Time", y=signal_name, kind="line", title=title)
    plt.show(block=True)

def main():
    decoded = decode_file(mymdf_file, dbc_file)
    trommelpos_df = get_single_channel_df(decoded, "General_LD_TrommelPositoin")
    print_signal(trommelpos_df)

def sonstiges():
        decoded = decode_file(mymdf_file,dbc_file)
        ch_grps = [ chg.keys() for chg in decoded.iter_groups()]
        channels = [ ch for ch in decoded.channels_db.keys()]
        startzeit = decoded.start_time

        for ch_grp in ch_grps:
            # print(ch_grp)
            print(ch_grp)
        for ch in channels:
            # print(ch_grp)
            print(ch)

        trommelPos = decoded.get("General_LD_TrommelPositoin")
        values = trommelPos.samples
        timestamps = [ startzeit + timedelta(seconds=t) for t in trommelPos.timestamps]

        print("Trommel-Position")
        print(values[:10])
        print(timestamps[:10])
        # for sig_val in decoded.

        # for ch in mdf.channels_db if "CAN"

main()
