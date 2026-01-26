from collections import defaultdict
from datetime import timedelta
from zoneinfo import ZoneInfo

import logging
log = logging.getLogger("Cantransform")
import matplotlib.pyplot as plt
from os import path
from datetime import datetime, time

import pandas as pd

from asammdf import MDF
import cantools
from pandas.core.interchange.dataframe_protocol import DataFrame

dbc_file = "../tests/data/typ1.dbc"
mymdf_file = "../tests/data/typ1_bsp1.mf4"

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

def decode_files(mdf_file, dbc_file):
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
    df = decoded_mdf.to_dataframe(
        channels=[signal_name],
        time_as_date=True
    )
    return df

def get_signals_df(decoded_mdf: MDF, signal_names: list[str]):
    df = decoded_mdf.to_dataframe(
        channels=signal_names,
        time_as_date=True
    )
    print(df)
    return df

def get_available_signals(decoded_mdf: MDF) -> list[str]:
    available_signals = decoded_mdf.channels_db.keys()
    available_signals = [ sig for sig in available_signals if not (sig.__contains__(".") or sig.__eq__("time"))]
    return available_signals

def get_mdfs_min_max_time(decoded_mdfs: list[MDF]) :
    min_time = None
    max_time = None
    for mdf in decoded_mdfs:
        i_min, i_max = get_mdf_min_max_time(mdf)
        min_time = min(min_time, i_min) if min_time is not None else i_min
        max_time = max(max_time, i_max) if max_time is not None else i_max
    return min_time, max_time

def get_mdfs_min_max_time_approx(mdfs: list[MDF]) :
    min_time = None
    max_time = None
    for mdf in mdfs:
        start_time = mdf.start_time
        print(start_time)
        min_time = min(min_time, start_time) if min_time is not None else start_time
        max_time = max(max_time, start_time) if max_time is not None else start_time
    return min_time, max_time

def get_mdf_min_max_time(decoded_mdf: MDF) :
    startzeit = decoded_mdf.start_time
    df = decoded_mdf.to_dataframe(time_as_date=True, )
    min_time= to_cet(df.index[0])
    max_time= to_cet(df.index[-1])
    return min_time,max_time

def export_to_csv(filename: str, decoded_mdfs: list[MDF], selected_signals: list[str]):
    bsp_mdf = decoded_mdfs[0]
    channel_grp_signals = get_channel_group_signals(bsp_mdf, selected_signals)

    channel_grp_dfs = get_channel_grp_dfs(channel_grp_signals, decoded_mdfs)

    filenames = []
    for channel_grp in channel_grp_signals.keys():
        grp_filename = f'{filename[0:-4]}-ChGrp_{channel_grp}.csv'
        grp_mdfs_df = pd.concat(channel_grp_dfs[channel_grp],
                            axis=0
                            ).sort_index()

        grp_mdfs_df.to_csv(grp_filename, date_format="%Y-%m-%d %H:%M:%S.%f%z")
        filenames.append(grp_filename)

    return filenames


def get_channel_grp_dfs(channel_grp_signals: dict[int, list],
                        decoded_mdfs: list[MDF]) -> defaultdict[int, list]:
    channel_groups = channel_grp_signals.keys()
    channel_grp_dfs = defaultdict(list)

    for decoded_mdf in decoded_mdfs:
        decoded_mdf.start_time = to_cet(decoded_mdf.start_time)
        for channel_grp in channel_groups:
            channel_sigs = channel_grp_signals[channel_grp]
            mdf_df = decoded_mdf.to_dataframe(channels=channel_sigs, time_as_date=True, )
            channel_grp_dfs[channel_grp].append(mdf_df)
    return channel_grp_dfs


def get_channel_group_signals(reference_mdf: MDF, selected_signals: list[str]) -> dict[int, list]:
    channel_grp_signals = defaultdict(list)
    for sig in selected_signals:
        groups = reference_mdf.whereis(sig)
        if len(groups) != 1:
            log.error(f'Signal {sig} kommt in {len(groups)} Channelgruppen vor')
        if len(groups) == 0:
            continue
        group = groups[0][0]
        channel_grp_signals[group].append(sig)
    return channel_grp_signals

def to_cet(dt : datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo("Europe/Berlin"))


def print_signal(signal_df):
    signal_name = signal_df.columns[1]
    title = f'{signal_name} over Time'
    signal_df.plot(x="Time", y=signal_name, kind="line", title=title)
    plt.show(block=True)
