BASELINE_SECONDS = 3.0
CUE_SECONDS = 1.5
CROSS_SECONDS = 5.0
ITI_SECONDS = 1.5
END_SECONDS = 3.0
BEEP_FREQUENCY = 880

STAGE_BLANK = "blank"
STAGE_STIMULUS = "stimulus"
STAGE_CROSS = "cross"

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
TRIAL_SEQUENCES = {
    "motor_imagery": [
        ("BASELINE", BASELINE_SECONDS, STAGE_BLANK),
        ("CUE", CUE_SECONDS, STAGE_STIMULUS, beep()),
        ("CROSS", CROSS_SECONDS, STAGE_CROSS),
        ("ITI", ITI_SECONDS, STAGE_BLANK),
    ],
    "action_words": [
        ("BASELINE", BASELINE_SECONDS, STAGE_BLANK),
        ("CUE", CUE_SECONDS, STAGE_STIMULUS, beep()),
        ("CROSS", CROSS_SECONDS, STAGE_CROSS),
        ("ITI", ITI_SECONDS, STAGE_BLANK),
    ],
    "motor_observation": [
        ("BASELINE", BASELINE_SECONDS, STAGE_BLANK),
        ("CUE", CUE_SECONDS, STAGE_STIMULUS, beep()),
        ("CROSS", CROSS_SECONDS, STAGE_CROSS),
        ("ITI", ITI_SECONDS, STAGE_BLANK),
    ],
    "mix": [
        ("BASELINE", BASELINE_SECONDS, STAGE_BLANK),
        ("CUE", CUE_SECONDS, STAGE_STIMULUS, beep()),
        ("CROSS", CROSS_SECONDS, STAGE_CROSS),
        ("ITI", ITI_SECONDS, STAGE_BLANK),
    ],
}
