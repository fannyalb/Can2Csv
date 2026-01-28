import os

import pandas as pd
from asammdf import MDF
import pandas as pd

from asammdf import MDF

import src.cantransform
from src.calculations import *

logging.basicConfig(level=logging.DEBUG)

TEST_DBC_LW_FILE = "data/typ2.dbc"
TEST_DBC_SW_FILE = "data/typ1.dbc"
TEST_DECODED_MDF_FILE_LW = "data/typ2_bsp1_decoded.mf4"
TEST_DECODED_MDF_FILE_LW_2 = "data/typ2_bsp2_decoded.mf4"
TEST_DECODED_MDF_FILE_LW_3 = "data/typ2_bsp3_decoded_gewichte.mf4"
TEST_DECODED_MDF_FILE_SW = "data/typ1_bsp2_decoded.mf4"


def test_print_weight():
    weight_signal = "General_LD_MeassuredWeight"
    speed_signal = "MotorDrive_LD_ActualSpeed"
    speed_signal = "MotorLift_LD_ActualSpeed"
    signals = [weight_signal, speed_signal]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW)
    mdf_df = decoded_mdf.to_dataframe(channels=[weight_signal], time_as_date=True)
    src.cantransform.print_signal(mdf_df)


def test_print_speed():
    weight_signal = "General_LD_MeassuredWeight"
    speed_signal = "MotorDrive_LD_ActualSpeed"
    signals = [weight_signal, speed_signal]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW)
    mdf_df = decoded_mdf.to_dataframe(channels=[speed_signal], time_as_date=True)
    src.cantransform.print_signal(mdf_df)


def test_print_all():
    weight_signal = "General_LD_MeassuredWeight"
    speed_signal = "MotorDrive_LD_ActualSpeed"
    signals = [weight_signal, speed_signal]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW)
    mdf_df = decoded_mdf.to_dataframe(channels=[weight_signal, speed_signal], time_as_date=True)
    src.cantransform.print_signal(mdf_df)


def test_print_many_files():
    dbc_file = TEST_DBC_LW_FILE
    mdf_dir = "E:/BauerLadstaetter/Z-Laufwerk/C1667112/00000064"
    mdf_paths = [
        os.path.join(root, f)
        for root, _, files in os.walk(mdf_dir)
        for f in files
        if f.lower().endswith(".mf4")
    ]
    weight_signal = "General_LD_MeassuredWeight"
    speed_signal = "MotorDrive_LD_ActualSpeed"
    speed_signal = "MotorLift_LD_ActualSpeed"
    decoded_mdfs = [src.cantransform.decode_file(mdf, dbc_file) for mdf in mdf_paths[:10]]
    dataframes = [ mdf.to_dataframe(channels=[weight_signal, speed_signal],time_as_date=True, raster=1) for mdf in decoded_mdfs]
    all_in_one_df = pd.concat(dataframes,
                            axis=0
                            ).sort_index()
    print(all_in_one_df)
    src.cantransform.print_2_signals(all_in_one_df)

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

def test_berechne_distanz_laufwagen_aus_lifting_position():
    speed_signal = "MotorLift_LD_ActualSpeed"
    sig_lift_pos = "General_LD_LiftingPosition" # 1 entspricht viertel-umdrehung der winde
    signals = [speed_signal, sig_lift_pos]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW)
    dataframe = decoded_mdf.to_dataframe(channels=signals, time_as_date=True)

    result = berechne_laufwagen_distanz(dataframe, aus_liftpos=True)
    gesamtdistanz = result["lw_strecke_gesamt_m"].tail(1).iloc[0]
    pull = result["lw_strecke_pull"].tail(1)[0]
    release = result["lw_strecke_release"].tail(1)[0]
    print(f'Gesamtdistanz (Zuzug, Ausspulen) LW: {gesamtdistanz}')
    print(f'Distanz Zuzug LW: {pull}')
    print(f'Distanz Ausspulen LW: {release}')
    assert round(pull, 1) >= 6.5 and round(pull, 1) <= 6.7
    assert round(release, 1) >= 4.3 and round(release, 1) <= 4.5
    assert round(gesamtdistanz, 1) >= 10.8 and round(gesamtdistanz, 1) <= 11.2


def test_berechne_distanz_laufwagen_aus_motorgeschwindikeit():
    speed_signal = "MotorLift_LD_ActualSpeed"
    sig_lift_pos = "General_LD_LiftingPosition" # 1 entspricht viertel-umdrehung der winde
    signals = [speed_signal, sig_lift_pos]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW)
    dataframe = decoded_mdf.to_dataframe(channels=signals, time_as_date=True)

    result = berechne_laufwagen_distanz(dataframe, aus_liftpos=False)
    gesamtdistanz = result["lw_strecke_gesamt_m"].tail(1).iloc[0]
    pull = result["lw_strecke_pull"].tail(1)[0]
    release = result["lw_strecke_release"].tail(1)[0]
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
    sig_weight = "General_LD_MeassuredWeight" # 1 entspricht viertel-umdrehung der winde
    signals = [sig_weight]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW_2)
    dataframe = decoded_mdf.to_dataframe(channels=signals, time_as_date=True)

    result = berechne_gewicht(dataframe)
    gewicht = result["lw_weight_kg"].tail(1).iloc[0]
    print(f'Gewichte: {result["lw_weight_kg"]}')
    print(f'Gesamtgewicht kg LW: {gewicht}')
    assert gewicht == 99

def test_berechne_gewicht_in_bewegung():
    sig_weight = "General_LD_MeassuredWeight" # 1 entspricht viertel-umdrehung der winde
    speed_signal = "MotorDrive_LD_ActualSpeed"
    signals = [sig_weight, speed_signal]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW_3)
    dataframe = decoded_mdf.to_dataframe(channels=signals, time_as_date=True)

    result = berechne_gewicht_in_bewegung(dataframe)
    gewicht = result["lw_weight_mov_cumsum"].tail(1).iloc[0]
    aktuelle_gewichte = result["lw_weight_mov_current"]
    # print(f'Events: {events.where(events["lw_weight_mov_events"] > 0)}')
    # print(f'Gewichte: {aktuelle_gewichte.tolist()}')
    print(f'Gesamtgewicht kg LW: {gewicht}')
    assert gewicht == 2165
