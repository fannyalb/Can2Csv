import asammdf
import pytest
from asammdf import MDF
from src.decode_mf4 import *
import pandas as pd

# Beispiel-Mockdateien (können kleine Testdateien sein)
TEST_MDF_FILE = "data/beispiel1.mf4"
TEST_DBC_FILE = "data/beispiel1.dbc"
TEST_DECODED_MDF_FILE = "data/beispiel1_decoded.mf4"
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

    # Prufen, dass Dataframe 2 Spalten hat
    assert len(signal_df.columns) == 2

    # Time-Spalte ist vorhanden
    assert "Time" in signal_df.columns
    # TEST-Spalte ist vorhanden
    assert TEST_SIGNAL_TROMMEL_POS in signal_df.columns
    # 2️⃣ Prüfen, dass 2998 Signale da sind
    assert len(signal_df) == 2999

    assert signal_df.loc[0, TEST_SIGNAL_TROMMEL_POS] == -10286

