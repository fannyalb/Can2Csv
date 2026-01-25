import asammdf
import pytest
from asammdf import MDF
from src.cantransform import *
import pandas as pd

# Beispiel-Mockdateien (können kleine Testdateien sein)
TEST_MDF_FILE = "data/beispiel1.mf4"
TEST_DBC_FILE = "data/beispiel1.dbc"
TEST_DECODED_MDF_FILE = "data/beispiel1_decoded.mf4"
TEST_DECODED_MDF_FILE2 = "data/typ1_bsp2_decoded.mf4"
TEST_SIGNAL_TROMMEL_POS = "General_LD_TrommelPositoin"


def test_decode_file_returns_mdf_object():
    decoded_mdf = decode_file(TEST_MDF_FILE, TEST_DBC_FILE)

    # 1️⃣ Prüfen, dass ein MDF-Objekt zurückkommt
    assert isinstance(decoded_mdf, MDF)

    # 2️⃣ Prüfen, dass mindestens ein Signal vorhanden ist
    assert len(decoded_mdf.channels_db) > 0

    # 3️⃣ Optional: ein bekanntes Signal existiert
    assert TEST_SIGNAL_TROMMEL_POS in decoded_mdf.channels_db

    # 4️⃣ Optional: Signal-Timestamps und Werte sind nicht leer
    signal = decoded_mdf.get(TEST_SIGNAL_TROMMEL_POS)
    assert len(signal.samples) > 0
    assert len(signal.timestamps) > 0


def test_get_single_channel_df():
    decoded_mdf = MDF(TEST_DECODED_MDF_FILE)
    signal_df = get_single_channel_df(decoded_mdf, TEST_SIGNAL_TROMMEL_POS)

    # Pruefen of Dataframe zurueckkommt
    assert isinstance(signal_df, pd.DataFrame)

    print(signal_df.columns)
    # Prufen, dass Dataframe 1 Spalte hat
    assert len(signal_df.columns) == 1

    # TEST-Spalte ist vorhanden
    assert TEST_SIGNAL_TROMMEL_POS in signal_df.columns
    # 2️⃣ Prüfen, dass 2999 Signale da sind
    assert len(signal_df) == 2999

    assert signal_df.iloc[0][TEST_SIGNAL_TROMMEL_POS] == -10286


def test_get_available_signals():
    decoded_mdf = MDF(TEST_DECODED_MDF_FILE)
    result = get_available_signals(decoded_mdf)
    print(f'Signals {result}')

    assert len(result) == 11


def test_get_mdf_min_max_datetime():
    fmt_string = "%Y-%m-%d %H:%M:%S.%f%z"
    soll_min = to_cet(datetime.strptime("2025-12-17 10:05:00.025550+0100", fmt_string))
    soll_max = to_cet(datetime.strptime("2025-12-17 10:09:59.936750+0100", fmt_string))

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE)
    (min_dt, max_dt) = get_mdf_min_max_time(decoded_mdf)

    print(f'Min: {min_dt}')
    print(f'Max: {max_dt}')
    assert soll_min == min_dt
    assert soll_max == max_dt


def test_get_mdfs_min_max_time():
    fmt_string = "%Y-%m-%d %H:%M:%S.%f%z"
    soll_min = to_cet(datetime.strptime("2025-12-17 10:05:00.025550+0100", fmt_string))
    soll_max = to_cet(datetime.strptime("2025-12-17 14:29:59.987400+0100", fmt_string))

    decoded_mdf1 = MDF(TEST_DECODED_MDF_FILE)
    decoded_mdf2 = MDF(TEST_DECODED_MDF_FILE2)
    mdfs = [decoded_mdf1, decoded_mdf2]
    (min_dt, max_dt) = get_mdfs_min_max_time(mdfs)

    print(f'Min: {min_dt}')
    print(f'Max: {max_dt}')
    assert soll_min == min_dt
    assert soll_max == max_dt
