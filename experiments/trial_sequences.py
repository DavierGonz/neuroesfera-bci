BASELINE_SECONDS = 2.0
CUE_SECONDS = 1.0
ACTIVE_SECONDS = 4.0
REST_SECONDS = 2.0
END_SECONDS = 3.0
BEEP_FREQUENCY = 880

STAGE_BLANK = "blank"
STAGE_STIMULUS = "stimulus"
STAGE_ACTIVE = "active"
STAGE_REST = "rest"


def beep(start=0.0, duration=CUE_SECONDS, frequency=BEEP_FREQUENCY):
    return {
        "beep": {
            "start": start,
            "duration": duration,
            "frequency": frequency,
        }
    }


# Edita estas listas para cambiar el orden o duracion por experimento.
# Formato basico: ("MARCADOR", duracion_en_segundos, tipo_de_pantalla)
# Formato con bip: ("MARCADOR", duracion_en_segundos, tipo_de_pantalla, beep(...))
DEFAULT_TRIAL_SEQUENCE = [
    ("BASELINE", BASELINE_SECONDS, STAGE_BLANK),
    ("CUE", CUE_SECONDS, STAGE_STIMULUS, beep()),
    ("ACTIVE", ACTIVE_SECONDS, STAGE_ACTIVE),
    ("REST", REST_SECONDS, STAGE_REST),
]

TRIAL_SEQUENCES = {
    "experiment_1": DEFAULT_TRIAL_SEQUENCE,
    "experiment_2": DEFAULT_TRIAL_SEQUENCE,
    "experiment_3": DEFAULT_TRIAL_SEQUENCE,
    "paradigm_mi": DEFAULT_TRIAL_SEQUENCE,
    "paradigm_me": DEFAULT_TRIAL_SEQUENCE,
    "paradigm_mo": DEFAULT_TRIAL_SEQUENCE,
    "paradigm_aw": DEFAULT_TRIAL_SEQUENCE,
}
