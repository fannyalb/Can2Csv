import logging
import pandas as pd
from typing import List, Dict

from asammdf import MDF

logging.basicConfig(level=logging.DEBUG)

def mdf_to_list_dict(mdf: MDF, signals: list[str]) -> Dict[str, list[Dict]]:
    return mdfs_to_list_dict([mdf], signals)

def mdfs_to_list_dict(mdfs: list[MDF], signals: list[str]) -> Dict[str, list[Dict]]:
    machine_data = {}
    for sig in signals:
        sig_mdfs = []
        for mdf in mdfs:
            mdf_df = mdf.to_dataframe(channels=[sig]).reset_index()
            mdf_df = mdf_df.rename(columns={sig: "value"})
            sig_mdfs.append(mdf_df)
        machine_data[sig] = pd.concat(sig_mdfs, axis=0).sort_index().to_dict('records')
    return machine_data

def extract_weight_events(
        weight_data: List[Dict],
        speed_data: List[Dict],
        speed_threshold: float = 50,
        movement_window_s: float = 15.0,
        cooldown_s: float = 120.0,
        max_pre_seconds: float = 60.0,
        min_weight: float = 20,
        post_window_s: float = 5.0
) -> Dict:
    logging.info(f"[WEIGHT_EVENTS] Eingehende Punkte: weight={len(weight_data)}, speed={len(speed_data)}")

    if not weight_data or not speed_data:
        raise Exception("Daten fehlen")
        return {"total_weight": 0, "last_events": []}

    weight_sorted = sorted(weight_data, key=lambda x: x["timestamps"])
    speed_sorted = sorted(speed_data, key=lambda x: x["timestamps"])

    # Zeitbasis prüfen (Sekunden vs Millisekunden)
    # if weight_sorted[0]["timestamps"] > 1e10:
    #     for w in weight_sorted:
    #         w["timestamps"] /= 1000.0
    #     for s in speed_sorted:
    #         s["timestamps"] /= 1000.0

    # 1) Bewegungsperioden erkennen
    movements = []
    running = False
    run_start = None
    run_last_ts = None
    print(f"{len(speed_sorted)} speed-date")

    for s in speed_sorted:
        ts = s["timestamps"]
        val = s["value"]
        # print(f"Speed {s}")
        moving = abs(val) > speed_threshold

        if moving:
            # print(f"Moving: Geschwindigkeit: {val}")
            if not running:
                running = True
                run_start = ts
            run_last_ts = ts
        else:
            # print(f'Not Moving: Geschwindigkeit : {abs(val)}')
            if running:
                duration = run_last_ts - run_start if run_last_ts is not None else 0
                if duration >= movement_window_s:
                    movements.append({"start": run_start, "end": run_last_ts})
                    logging.info(f"[RUN FOUND] start={run_start}, end={run_last_ts}, duration={duration}s")
                    print(f"[RUN FOUND] start={run_start}, end={run_last_ts}, duration={duration}s")
                running = False
                run_start = None
                run_last_ts = None

    # letzter laufender Run
    if running and run_start is not None and run_last_ts is not None:
        duration = run_last_ts - run_start
        if duration >= movement_window_s:
            movements.append({"start": run_start, "end": run_last_ts})
            logging.info(f"[RUN FOUND] start={run_start}, end={run_last_ts}, duration={duration}s")

    # 2) Events bestimmen
    events = []
    last_event_time = -float("inf")
    last_weight_below_threshold = True  # Flag: Gewicht unter min_weight seit letztem Event
    weight_idx = len(weight_sorted) - 1

    for mv in movements:
        mv_start = mv["start"]
        mv_end = mv["end"]

        # laufendes Flag updaten: Gewicht seit letztem Event unter min_weight?
        for w in weight_sorted:
            if w["timestamps"] > last_event_time and w["value"] < min_weight:
                last_weight_below_threshold = True

        if mv_start < last_event_time + cooldown_s:
            continue

        candidate = None

        # a) Gewicht vor Run suchen
        while weight_idx >= 0 and weight_sorted[weight_idx]["timestamps"] >= mv_start:
            weight_idx -= 1
        idx = weight_idx
        while idx >= 0:
            w = weight_sorted[idx]
            if w["timestamps"] < mv_start - max_pre_seconds:
                break
            if w["value"] is not None and w["value"] >= min_weight:
                candidate = {"timestamps": w["timestamps"], "weight": w["value"]}
                logging.info(f"[EVENT BEFORE RUN] gefunden: {candidate}")
                break
            idx -= 1

        # b) Falls kein Gewicht vor Run, Gewicht während Run suchen
        if not candidate:
            for w in weight_sorted:
                if mv_start <= w["timestamps"] <= mv_end and w["value"] >= min_weight:
                    candidate = {"timestamps": w["timestamps"], "weight": w["value"]}
                    logging.info(f"[EVENT DURING RUN] gefunden: {candidate}")
                    break

        # c) Falls immer noch keins, Gewicht kurz nach Run-Ende prüfen
        if not candidate:
            for w in weight_sorted:
                if mv_end < w["timestamps"] <= mv_end + post_window_s and w["value"] >= min_weight:
                    candidate = {"timestamps": w["timestamps"], "weight": w["value"]}
                    logging.info(f"[EVENT AFTER RUN] gefunden: {candidate}")
                    break

        if candidate:
            if last_weight_below_threshold:
                print("Gefunden")
                events.append(candidate)
                last_event_time = candidate["timestamps"]
                last_weight_below_threshold = False  # Reset-Flag zurücksetzen
            else:
                logging.info(
                    f"[EVENT IGNORED] Gewicht noch über min_weight seit letztem Event für Run {mv_start}-{mv_end}")
                print(
                    f"[EVENT IGNORED] Gewicht noch über min_weight seit letztem Event für Run {mv_start}-{mv_end}")
        else:
            print(f"[EVENT] Kein passendes Gewicht für Run {mv_start}-{mv_end}")

    # 3) Ergebnis zusammenstellen
    events = sorted(events, key=lambda x: x["timestamps"])
    total_weight = sum(e.get("weight", 0) for e in events)

    summary = {
        "total_weight": total_weight,
        "last_events": events[-10:],  # letzte 10 für Tabelle
        "all_events": events  # alle für Graph
    }

    logging.info(f"[WEIGHT_EVENTS] Ergebnis: {summary}")
    return summary


def calculate_distance(
        rpm_data: List[Dict],
        min_rpm: float = 1.0,
        max_gap_s: float = 60.0,
        drum_diameter_m: float = 0.5
) -> Dict:
    """
    Berechnet die kumulierte Strecke aus Trommel-RPM-Daten.

    Args:
        rpm_data: Liste von Dicts [{"timestamps": float, "value": float}, ...]
        min_rpm: Minimaler RPM-Wert, alles darunter wird als 0 ignoriert
        max_gap_s: Maximaler Zeitschritt, größere Lücken werden übersprungen
        drum_diameter_m: Durchmesser der Trommel in Metern (0.5 m Standard)

    Returns:
        Dict mit:
            - total_distance: Summe der Strecke in Metern
            - increments: Liste der Strecken pro Intervall (Meter)
    """
    import logging
    import math

    if not rpm_data:
        logging.info("[DISTANCE] Keine RPM-Daten vorhanden")
        return {"total_distance": 0.0, "increments": []}

    # 1) sortieren nach Timestamp
    rpm_sorted = sorted(rpm_data, key=lambda x: x["timestamps"])
    timestamps = [x["timestamps"] for x in rpm_sorted]
    values = [x["value"] for x in rpm_sorted]

    # 2) prüfen ob Timestamp in ms statt s
    if timestamps[0] > 1e10:
        timestamps = [t / 1000.0 for t in timestamps]

    # 3) Betrag und Threshold
    rpm_abs = [abs(v) if abs(v) >= min_rpm else 0.0 for v in values]

    # 4) Umrechnen in Umdrehungen pro Sekunde
    rev_s = [v / 60.0 for v in rpm_abs]

    # 5) Berechnung der Intervalle
    increments = []
    total_distance = 0.0
    U = math.pi * drum_diameter_m  # Trommelumfang

    for i in range(len(rev_s) - 1):
        dt = timestamps[i + 1] - timestamps[i]
        if dt <= 0 or dt > max_gap_s:
            continue  # ungültige Intervalle überspringen
        delta_rev = (rev_s[i] + rev_s[i + 1]) / 2.0 * dt
        delta_s = delta_rev * U
        increments.append(delta_s)
        total_distance += delta_s

    logging.info(f"[DISTANCE] total_distance={total_distance:.2f} m, intervals={len(increments)}")
    return {"total_distance": total_distance, "increments": increments}


# --- NEU: Laufwägen Strecke ---
def calculate_lift_distance(
        speed_data: List[Dict],
        min_rpm: float = 1.0,
        max_gap_s: float = 60.0,
        drum_diameter_m: float = 0.28,
        i: float = 60.0
) -> Dict:
    import math
    import logging

    if not speed_data:
        return {"total_pull": 0.0, "total_release": 0.0, "increments_pull": [], "increments_release": []}

    data_sorted = sorted(speed_data, key=lambda x: x["timestamps"])
    timestamps = [dp["timestamps"] for dp in data_sorted]
    rpm_values = [dp["value"] for dp in data_sorted]

    if timestamps[0] > 1e10:
        timestamps = [t / 1000.0 for t in timestamps]

    U = math.pi * drum_diameter_m

    total_pull = 0.0
    total_release = 0.0
    increments_pull = []
    increments_release = []

    for i in range(len(rpm_values) - 1):
        rpm_motor_0 = rpm_values[i]
        rpm_motor_1 = rpm_values[i + 1]

        if rpm_motor_0 is None or rpm_motor_1 is None:
            continue

        rpm_drum_0 = rpm_motor_0 / i
        rpm_drum_1 = rpm_motor_1 / i

        if abs(rpm_drum_0) < min_rpm:
            rpm_drum_0 = 0.0
        if abs(rpm_drum_1) < min_rpm:
            rpm_drum_1 = 0.0

        dt = timestamps[i + 1] - timestamps[i]
        if dt <= 0 or dt > max_gap_s:
            continue

        delta_rev = (rpm_drum_0 + rpm_drum_1) / 2.0 * dt / 60.0
        delta_s = delta_rev * U

        if delta_s >= 0:
            total_pull += delta_s
            increments_pull.append(delta_s)
        else:
            total_release += abs(delta_s)
            increments_release.append(abs(delta_s))

    logging.info(
        f"[LIFT_DISTANCE] Pull={total_pull:.2f} m, Release={total_release:.2f} m, Intervals={len(increments_pull) + len(increments_release)}")
    return {
        "total_pull": total_pull,
        "total_release": total_release,
        "increments_pull": increments_pull,
        "increments_release": increments_release
    }
