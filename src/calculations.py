from src.cantransform import *

import pandas as pd
import numpy as np

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("Calcs")
log.setLevel(logging.DEBUG)


def berechne_schlittenwinde_distanz(df: pd.DataFrame,
                                    trommel_durchmesser_m=0.5):
    sig_rpm = "General_LD_TrommelSpeed"
    if sig_rpm not in df.columns:
        raise Exception(f"Channel {sig_rpm} nicht in dataframe")

    umfang = np.pi * trommel_durchmesser_m
    freq = df[sig_rpm] / 60.0 # Umdrehungen pro Sek
    v_lin = abs(freq * umfang)

    # Zurueckgelegte Strecke
    # s1 = s0 + v1 * dt1
    result = pd.DataFrame(index=df.index)
    dt = df.index.to_series().diff().dt.total_seconds()
    dt.iloc[0] = 0.0

    result["sw_strecke_current_m"] = (v_lin * dt)
    result["sw_strecke_cumsum_m"] = (v_lin * dt).cumsum()
    return result

def berechne_laufwagen_distanz(df: pd.DataFrame,
                               trommel_durchmesser_m=0.28,
                               aus_liftpos=False) -> pd.DataFrame:
    # Wenn aus_liftpos == true -> Berechnung aus Liftpos
    # Sonst Berechnung aus Motorgeschwindigkeit ("MotorLift")
    result_df = df
    delta_strecke_lastseil: pd.DataFrame
    if aus_liftpos:
        delta_strecke_lastseil = (
            streckendelta_lastseil_aus_liftpos(df, trommel_durchmesser_m))
    else:
        getriebeuebersetzung=60
        delta_strecke_lastseil = (
            streckendelta_lastseil_aus_motorspeed(df,
                                                  trommel_durchmesser_m,
                                                  getriebeuebersetzung))

    ds_release = delta_strecke_lastseil.clip(lower=0)       # if i < 0 : i = 0
    ds_pull = abs(delta_strecke_lastseil.clip(upper=0))   # if i > 0 : i = 0

    result_df["lw_ds_m"] = delta_strecke_lastseil
    # Streckenaenderung Zuzug
    result_df["lw_ds_pull_m"] = ds_pull
    # Streckenaenderung Auslass
    result_df["lw_ds_release"] = ds_release
    # Zuzug kumulierte Summe
    result_df["lw_strecke_pull"] = ds_pull.cumsum()
    # Ablass kumulierte Summe
    result_df["lw_strecke_release"] = abs(ds_release).cumsum() # if i > 0 : i = 0
    # Gesamtdistanz kumulierte Summe
    result_df["lw_strecke_gesamt_m"] = abs(delta_strecke_lastseil).cumsum()
    return result_df


def streckendelta_lastseil_aus_liftpos(df: pd.DataFrame,
                                       trommel_durchmesser_m: float) -> pd.DataFrame:
    sig_lift_pos = "General_LD_LiftingPosition" # 1 entspricht 1/4-umdrehung der winde
    if sig_lift_pos not in df.columns:
        raise Exception(f"Channel {sig_lift_pos} nicht in dataframe")

    # General_LD_LiftingPosition => Änderung von 1 entspricht 1/4 Umdrehung der Winde
    # Pro 1 Änderung -> Änderung der Strecke des Lastseils = 1/4 Trommelumfang
    trommel_umfang_m = trommel_durchmesser_m * np.pi
    # Streckenaenderung des Lastseils
    streckendelta = df[sig_lift_pos].diff() * trommel_umfang_m/4
    # Vorzeichen anders als bei Motorspeed
    streckendelta = -streckendelta
    return streckendelta


def streckendelta_lastseil_aus_motorspeed(df: pd.DataFrame,
                                          trommel_durchmesser_m: float,
                                          getriebeuebersetzung=60
                                          ):
    sig_rpm_motor = "MotorLift_LD_ActualSpeed"
    if sig_rpm_motor not in df.columns:
        raise Exception(f"Channel {sig_rpm_motor} nicht in dataframe")

    umfang = np.pi * trommel_durchmesser_m
    rpm_trommel = df[sig_rpm_motor] / getriebeuebersetzung
    freq = rpm_trommel / 60.0           # Umdrehungen pro Sek
    v_lin = freq * umfang               # Lineare Geschwindikeit
    # Zurueckgelegte Strecke
    # s1 = s0 + v1 * dt1

    dt = df.index.to_series().diff().dt.total_seconds()
    dt.iloc[0] = 0.0

    # Streckenaenderung des Lastseils
    streckendelta = (v_lin * dt)
    return streckendelta


def berechne_gewicht(df: pd.DataFrame):
    sig_weight = "General_LD_MeassuredWeight"
    if sig_weight not in df.columns:
        raise Exception(f"Channel {sig_weight} nicht in dataframe")

    # Zeitraeume, wo eine Gewichtsmessung stattfindet
    # -> Erkennung: Gewichtsaenderung
    ist_neuer_block =df[sig_weight] != df[sig_weight].shift()
    messungen = df[sig_weight]
    mess_bloecke = (messungen * ist_neuer_block).cumsum()
    gewicht_pro_block = (
        df[sig_weight]
        .groupby(mess_bloecke)
        .transform("first")
        .fillna(0)
    )

    gewichte_aufsummiert = (gewicht_pro_block * ist_neuer_block).cumsum()
    df["lw_weight_kg"] = gewichte_aufsummiert
    return df

def berechne_gewicht_in_bewegung(dframe: pd.DataFrame,
                                 zeitfenster_min_s=15,
                                 speed_abs_min_rpm=50,
                                 min_weight=20):
    sig_weight = "General_LD_MeassuredWeight"
    sig_speed = "MotorDrive_LD_ActualSpeed"
    if sig_weight not in dframe.columns:
        raise Exception(f"Channel {sig_weight} nicht in dataframe")
    if sig_speed not in dframe.columns:
        raise Exception(f"Channel {sig_speed} nicht in dataframe")

    min_duration = zeitfenster_min_s
    df = dframe.copy()

    # Bewegung erkennen
    is_moving = abs(df[sig_speed]) > speed_abs_min_rpm

    # Bewegungsblöcke
    block_id = (is_moving != is_moving.shift(fill_value=False)).cumsum()
    df["_block_id"] = block_id

    # Bewegungsdauer pro Block
    movement_blocks = (
        df[is_moving]
        .groupby("_block_id")
        .agg(
            start_time=(sig_speed, lambda s: s.index[0]),
            end_time=(sig_speed, lambda s: s.index[-1]),
        )
    )

    movement_blocks["duration"] = (
            movement_blocks["end_time"] - movement_blocks["start_time"]
    ).dt.total_seconds()

    # Gültige Bewegungen
    valid_blocks = movement_blocks[
        movement_blocks["duration"] >= min_duration
        ].index

    # Bewegungsstart (nur gültige)
    movement_start = (
            is_moving &
            (~is_moving.shift(fill_value=False)) &
            (df["_block_id"].isin(valid_blocks))
    )

    # Gewicht zum Bewegungsstart zählen
    df["lw_weight_mov_current"] = df[sig_weight].where(
        movement_start & (df[sig_weight] > min_weight),
        0.0
    )

    #  Kumulierte Summe
    df["lw_weight_mov_cumsum"] = df["lw_weight_mov_current"].cumsum()

    # Aufräumen
    df.drop(columns="_block_id", inplace=True)

    return df

    df["lw_weight_mov_current_kg"] = weight_current
    df["lw_weight_mov_sum_kg"] = pd.Series(gewichte_summiert, index=df.index).cumsum()
    return df