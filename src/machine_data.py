from enum import Enum

class Schlittenwinde(Enum):
    DISTANCE_DELTA = "sw_strecke_delta_m"
    DISTANCE_CUMSUM = "sw_strecke_cumsum_m"

class Laufwagen(Enum):
    # Gewichte, die waehrend Bewegung des LW gemessen wurden
    WEIGHT_MOV_CUR = "lw_weight_mov_current_kg"
    WEIGHT_MOV_CUMSUM = "lw_weight_mov_cumsum_kg"
    # Alle gemessenen Gewichte
    WEIGHT_CUMSUM = "lw_weight_kg"
    ROPE_DISTANCE_DELTA = "lw_rope_delta_m"
    # Streckenaenderung Zuzug
    ROPE_PULL_DELTA = "lw_rope_pull_delta_m"
    # Streckenaenderung Auslass
    ROPE_RELEASE_DELTA = "lw_rope_release_delta_m"
    # Zuzug kumulierte Summe
    ROPE_PULL_CUMSUM = "lw_rope_pull_cumsum_m"
    # Ablass kumulierte Summe
    ROPE_RELEASE_CUMSUM = "lw_rope_release_cumsum_m"
    # Gesamtdistanz kumulierte Summe
    ROPE_DISTANCE_CUMSUM = "lw_rope_cumsum_m"
    # Zurueckgelegte Strecke am Tragseil (Deltas)
    DISTANCE_DELTA = "lw_strecke_delta_m"
    # Zurueckgelegte Strecke am Tragseil (Deltas aufsummiert)
    DISTANCE_CUMSUM = "lw_strecke_cumsum_m"
    # Zurueckgelegte Strecke am Tragseil nach oben (Deltas)
    DISTANCE_UP_DELTA = "lw_strecke_up_delta_m"
    DISTANCE_UP_CUMSUM = "lw_strecke_up_cumsum_m"
    # Zurueckgelegte Strecke am Tragseil nach unten (Deltas)
    DISTANCE_DOWN_DELTA = "lw_strecke_down_delta_m"
    DISTANCE_DOWN_CUMSUM = "lw_strecke_down_cumsum_m"
    SIG_RPM_LIFT_MOTOR = "MotorLift_LD_ActualSpeed"
    SIG_RPM_DRIVE_MOTOR = "MotorLift_LD_ActualSpeed"
    SIG_MEASURED_WEIGHT = "General_LD_MeassuredWeight"
    SIG_STATE_OF_CHARGE = "Gerneral_LD_StateOfCharge"
