import os
import pytest
import logging

import pandas as pd
from asammdf import MDF
import pandas as pd

from asammdf import MDF

from machine_data import Laufwagen
from calculations import *

logging.basicConfig(level=logging.DEBUG)

TEST_DBC_LW_FILE = "data/typ2.dbc"
TEST_DBC_SW_FILE = "data/typ1.dbc"
TEST_DECODED_MDF_FILE_LW = "data/typ2_bsp1_decoded.mf4"
TEST_DECODED_MDF_FILE_LW_2 = "data/typ2_bsp2_decoded.mf4"
TEST_DECODED_MDF_FILE_LW_3 = "data/typ2_bsp3_decoded_gewichte.mf4"
TEST_DECODED_MDF_FILE_LW_4 = "data/typ2_bsp4_decoded.mf4"
TEST_DECODED_MDF_FILE_SW = "data/typ1_bsp2_decoded.mf4"


def test_berechne_distanz_schlittenwinde():
    speed_signal = "General_LD_TrommelSpeed"
    signals = [speed_signal]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_SW)

    result = berechne_schlittenwinde_distanz(decoded_mdf.to_dataframe(channels=[speed_signal], time_as_date=True))
    # print(result)
    gesamtdistanz = result["sw_strecke_cumsum_m"].tail(1)[0]
    print(f'Gesamtdistanz SW: {gesamtdistanz}')
    assert gesamtdistanz  >  116.00
    assert gesamtdistanz  <  117.00

def test_berechne_distanz_laufwagen():
    speed_signal_rope = "General_LD_CarryRopeDriveSpeed"
    speed_signal = "MotorDrive_LD_ActualSpeed"

    signals = [speed_signal_rope, speed_signal]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW_4)

    result = berechne_laufwagen_distanz(decoded_mdf.to_dataframe(channels=signals, time_as_date=True))
    # print(result)
    gesamtdistanz = result[Laufwagen.DISTANCE_CUMSUM.value].tail(1)[0]
    up = result["lw_strecke_up_cumsum_m"].tail(1)[0]
    down = result["lw_strecke_down_cumsum_m"].tail(1)[0]
    print(f'Gesamtdistanz LW: {gesamtdistanz}')
    print(f'Up LW: {up}')
    print(f'Down LW: {down}')
    assert gesamtdistanz == 49.0
    assert up == 49.0
    assert down == 0.0

def test_berechne_distanz_laufwagen_lastseil_aus_lifting_position():
    speed_signal = "MotorLift_LD_ActualSpeed"
    sig_lift_pos = "General_LD_LiftingPosition" # 1 entspricht viertel-umdrehung der winde
    signals = [speed_signal, sig_lift_pos]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW)
    dataframe = decoded_mdf.to_dataframe(channels=signals, time_as_date=True)

    result = berechne_laufwagen_distanz_seil(dataframe, aus_liftpos=True)
    gesamtdistanz = result["lw_rope_cumsum_m"].tail(1).iloc[0]
    pull = result["lw_rope_pull_cumsum_m"].tail(1)[0]
    release = result["lw_rope_release_cumsum_m"].tail(1)[0]
    print(f'Gesamtdistanz (Zuzug, Ausspulen) LW: {gesamtdistanz}')
    print(f'Distanz Zuzug LW: {pull}')
    print(f'Distanz Ausspulen LW: {release}')
    assert round(pull, 1) >= 6.5 and round(pull, 1) <= 6.7
    assert round(release, 1) >= 4.3 and round(release, 1) <= 4.5
    assert round(gesamtdistanz, 1) >= 10.8 and round(gesamtdistanz, 1) <= 11.2


def test_berechne_distanz_laufwagen_lastseil_aus_motorgeschwindikeit():
    speed_signal = "MotorLift_LD_ActualSpeed"
    sig_lift_pos = "General_LD_LiftingPosition" # 1 entspricht viertel-umdrehung der winde
    signals = [speed_signal, sig_lift_pos]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW)
    dataframe = decoded_mdf.to_dataframe(channels=signals, time_as_date=True)

    result = berechne_laufwagen_distanz_seil(dataframe, aus_liftpos=False)
    gesamtdistanz = result["lw_rope_cumsum_m"].tail(1).iloc[0]
    pull = result["lw_rope_pull_cumsum_m"].tail(1)[0]
    release = result["lw_rope_release_cumsum_m"].tail(1)[0]
    print(f'Gesamtdistanz (Zuzug, Ausspulen) LW: {gesamtdistanz}')
    print(f'Distanz Zuzug LW: {pull}')
    print(f'Distanz Ausspulen LW: {release}')
    assert round(pull, 1) >= 6.5 and round(pull, 1) <= 6.7
    assert round(release, 1) >= 4.3 and round(release, 1) <= 4.5
    assert round(gesamtdistanz, 1) >= 10.8 and round(gesamtdistanz, 1) <= 11.2


def test_berechne_gewicht():
    sig_weight = "General_LD_MeassuredWeight" # 1 entspricht viertel-umdrehung der winde
    signals = [sig_weight]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW)
    dataframe = decoded_mdf.to_dataframe(channels=signals, time_as_date=True)

    result = berechne_gewicht(dataframe)
    gewicht = result["lw_weight_kg"].tail(1).iloc[0]
    print(f'Gesamtgewicht kg LW: {gewicht}')
    assert gewicht == 46

def test_berechne_gewicht_2_messwerte():
    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW_2)
    dataframe = decoded_mdf.to_dataframe(time_as_date=True)

    result = berechne_gewicht(dataframe)
    gewicht = result["lw_weight_kg"].tail(1).iloc[0]
    print(f'Gewichte: {result["lw_weight_kg"]}')
    print(f'Gesamtgewicht kg LW: {gewicht}')
    assert gewicht == 99

def test_berechne_gewicht_in_bewegung_2_messwerte():
    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW_2)
    dataframe = decoded_mdf.to_dataframe(time_as_date=True)

    result = berechne_gewicht_in_bewegung(dataframe)
    gewicht = result["lw_weight_mov_cumsum_kg"].tail(1).iloc[0]
    print(f'Gewichte: {result["lw_weight_mov_cumsum_kg"]}')
    print(f'Gesamtgewicht kg LW: {gewicht}')
    assert gewicht == 40

def test_berechne_gewicht_in_bewegung():
    sig_weight = "General_LD_MeassuredWeight" # 1 entspricht viertel-umdrehung der winde
    speed_signal = "MotorDrive_LD_ActualSpeed"
    signals = [sig_weight, speed_signal]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW_3)
    dataframe = decoded_mdf.to_dataframe(channels=signals, time_as_date=True, raster=0.1)

    result = berechne_gewicht_in_bewegung(dataframe)
    gewicht = result["lw_weight_mov_cumsum_kg"].tail(1).iloc[0]
    aktuelle_gewichte = result["lw_weight_mov_current_kg"]