import csv
import os

import asammdf
import pytest
from asammdf import MDF
from src.cantransform import *
import pandas as pd

# Beispiel-Mockdateien (können kleine Testdateien sein)
TEST_MDF_FILE = "data/typ1_bsp1.mf4"
TEST_DBC_FILE = "data/typ1.dbc"
TEST_DECODED_MDF_FILE = "data/typ1_bsp1_decoded.mf4"
TEST_DECODED_MDF_FILE2 = "data/typ1_bsp2_decoded.mf4"
TEST_SIGNAL_TROMMEL_POS = "General_LD_TrommelPositoin"
TEST_BSP1_CSV_BATTERY_INFO = "data/beispiel1_batteryInfo.csv"


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


def test_export_to_csv_one_file():
    csv_filename="testoutput.csv"
    if path.isfile(csv_filename):
        os.remove(csv_filename)
    decoded_mdf = MDF(TEST_DECODED_MDF_FILE)
    signals =  ["Bat_ST_AvgVoltage", "Bat_ST_HighestCellTemp", "Bat_ST_LowestCellTemp", "Bat_ST_TotalCurrent"]
    result = export_to_csv("testoutput.csv", [decoded_mdf], signals)

    # expected = pd.read_csv(TEST_BSP1_CSV_BATTERY_INFO)
    actual = pd.read_csv(result[0])

    print(f'Actual: {actual}')
    assert actual['Bat_ST_AvgVoltage'] is not None
    assert actual['timestamps'][2] == "2025-12-17 10:05:00.225400+0100"
    assert actual['Bat_ST_AvgVoltage'][19] == 104.300000000000
    assert actual['Bat_ST_TotalCurrent'][18] == -0.5


def test_export_to_csv_2_files():
    csv_filename="testoutput2.csv"
    if path.isfile(csv_filename):
        os.remove(csv_filename)
    decoded_mdf = MDF(TEST_DECODED_MDF_FILE)
    decoded_mdf2= MDF(TEST_DECODED_MDF_FILE2)
    decoded_mdfs = [decoded_mdf,decoded_mdf2]
    signals = ["Bat_ST_AvgVoltage", "Bat_ST_HighestCellTemp", "Bat_ST_LowestCellTemp", "Bat_ST_TotalCurrent"]
    results = export_to_csv("testoutput2.csv", decoded_mdfs, signals)

    assert len(results) == 1
    assert results[0] is not None
    for csv_file in results:
        actual = pd.read_csv(csv_file)

        print(f'Actual: {actual}')
        assert actual['Bat_ST_AvgVoltage'] is not None
        assert actual['timestamps'][2] == "2025-12-17 10:05:00.225400+0100"
        assert actual['Bat_ST_AvgVoltage'][19] == 104.300000000000
        assert actual['Bat_ST_TotalCurrent'][18] == -0.5

def test_export_to_csv_2_channelgrps():
    # Separate Datei pro Channel-Group
    csv_filename = "testoutput3.csv"
    if path.isfile(csv_filename):
        os.remove(csv_filename)
    decoded_mdf = MDF(TEST_DECODED_MDF_FILE)
    decoded_mdf2 = MDF(TEST_DECODED_MDF_FILE2)
    decoded_mdfs = [decoded_mdf, decoded_mdf2]
    signals = ["Bat_ST_AvgVoltage", "MotorWinch_ST_ActualCurrent"]
    results = export_to_csv(csv_filename, decoded_mdfs, signals)

    assert len(results) == 2
    assert results[0] is not None
    csv_file = results[1]
    actual = pd.read_csv(csv_file)

    print(f'Actual: {actual}')
    assert actual['timestamps'][2998+1110-1] == '2025-12-17 14:26:50.996700+0100'
    assert actual['MotorWinch_ST_ActualCurrent'][2998 + 1110 - 1] == 31