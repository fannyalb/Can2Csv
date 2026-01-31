import os

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

    decoded_mdf = MDF(TEST_DECODED_MDF_FILE_LW_2)
    mdf_df = decoded_mdf.to_dataframe(channels=[weight_signal, speed_signal], time_as_date=True)
    mdf_df[speed_signal] = mdf_df[speed_signal] / 10
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
