import os

import pandas as pd
from asammdf import MDF

import src.cantransform
from src.alois_calculations import *

logging.basicConfig(level=logging.DEBUG)

TEST_DBC_LW_FILE = "data/typ2.dbc"
TEST_DBC_SW_FILE = "data/typ1.dbc"
TEST_DECODED_MDF_FILE_LW = "data/typ2_bsp1_decoded.mf4"
TEST_DECODED_MDF_FILE_LW_2 = "data/typ2_bsp2_decoded.mf4"
TEST_DECODED_MDF_FILE_SW = "data/typ1_bsp2_decoded.mf4"
TEST_DECODED_MDF_FILE_LW_3 = "data/typ2_bsp3_decoded_gewichte.mf4"
TEST_DECODED_MDF_FILE_LW_4 = "data/typ2_bsp4_decoded.mf4"


def test_extract_weight_events():
    weight_signal = "General_LD_MeassuredWeight"
    speed_signal = "MotorLift_LD_ActualSpeed"
    signals = [weight_signal, speed_signal]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW)
    machine_data = mdf_to_list_dict(decoded_mdf, signals)

    mdf_dict = machine_data
    weight_data = mdf_dict[weight_signal]
    speed_data = mdf_dict[speed_signal]
    result = extract_weight_events(weight_data, speed_data)
    print(result)


def test_extract_weight_events2():
    weight_signal = "General_LD_MeassuredWeight"
    speed_signal = "MotorLift_LD_ActualSpeed"
    signals = [weight_signal, speed_signal]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW_2)
    machine_data = mdf_to_list_dict(decoded_mdf, signals)

    mdf_dict = machine_data
    weight_data = mdf_dict[weight_signal]
    speed_data = mdf_dict[speed_signal]
    result = extract_weight_events(weight_data, speed_data)
    assert result["total_weight"] == 40


def test_extract_weight_events_more_files():
    dbc_file = TEST_DBC_LW_FILE
    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW_3)
    # mdf_dir = "E:/BauerLadstaetter/Z-Laufwerk/C1667112/00000032"
    # mdf_paths = [
    #     os.path.join(root, f)
    #     for root, _, files in os.walk(mdf_dir)
    #     for f in files
    #     if f.lower().endswith(".mf4")
    # ]
    weight_signal = "General_LD_MeassuredWeight"
    speed_signal = "MotorDrive_LD_ActualSpeed"
    # speed_signal = "MotorLift_LD_ActualSpeed"
    machine_data = mdf_to_list_dict(decoded_mdf, [weight_signal,speed_signal])

    weight_data = machine_data[weight_signal]
    speed_data = machine_data[speed_signal]
    result = extract_weight_events(weight_data, speed_data)
    print(result)


def test_extract_weight_events_all_files():
    dbc_file = TEST_DBC_LW_FILE
    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW_3)
    mdf_dir = "E:/BauerLadstaetter/Z-Laufwerk/C1667112/00000016"
    mdf_paths = [
        os.path.join(root, f)
        for root, _, files in os.walk(mdf_dir)
        for f in files
        if f.lower().endswith(".mf4")
    ]

    weight_signal = "General_LD_MeassuredWeight"
    speed_signal = "MotorDrive_LD_ActualSpeed"

    for mdf_file in mdf_paths:
        decoded_mdf = src.cantransform.decode_file(mdf_file, dbc_file)
        machine_data = mdf_to_list_dict(decoded_mdf, [weight_signal,speed_signal])
        if not (machine_data and len(machine_data) > 0):
            continue

        weight_data = machine_data[weight_signal]
        speed_data = machine_data[speed_signal]
        result = extract_weight_events(weight_data, speed_data)
        if result["total_weight"] > 0:
            print(f"{mdf_file} : {result['total_weight']}")


def test_extract_weight_events_more_files2():
    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW_4)
    weight_signal = "General_LD_MeassuredWeight"
    speed_signal = "MotorDrive_LD_ActualSpeed"
    signals = [weight_signal,speed_signal]

    mdf_dict = mdf_to_list_dict(decoded_mdf, signals)

    weight_data = mdf_dict[weight_signal]
    speed_data = mdf_dict[speed_signal]
    result = extract_weight_events(weight_data, speed_data)
    assert False

def test_calculate_distance_sw():
    speed_signal = "General_LD_TrommelSpeed"
    signals = [speed_signal]

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_SW)
    machine_data = mdf_to_list_dict(decoded_mdf, signals)

    mdf_dict = machine_data
    speed_data = mdf_dict[speed_signal]
    result = calculate_distance(speed_data)
    print(result)



def test_print_weight():
    weight_signal = "General_LD_MeassuredWeight"
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