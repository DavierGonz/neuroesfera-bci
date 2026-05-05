TARGETS = {
    "arm_vs_leg": {
        "code": "AL",
        "slug": "arm_vs_leg",
        "label": "Arm vs Leg",
    },
    "left_vs_right": {
        "code": "LR",
        "slug": "left_vs_right",
        "label": "Left vs Right",
    },
}

TARGET_KEYS = ["arm_vs_leg", "left_vs_right"]


STIMULUS_GENDERS = {
    "hombre": {
        "code": "H",
        "label": "Hombre",
    },
    "mujer": {
        "code": "M",
        "label": "Mujer",
    },
}

STIMULUS_GENDER_KEYS = ["hombre", "mujer"]


PROTOCOLS = {
    "motor_imagery": {
        "code": "MI",
        "slug": "mi",
        "label": "Motor Imagery",
        "menu_label": "Experimento 1",
        "setup_title": "Configuracion de Experimento 1",
        "implemented": True,
        "total_trials_multiplier": 2,
    },
    "action_words": {
        "code": "AW",
        "slug": "aw",
        "label": "Action Words",
        "menu_label": "Experimento 2",
        "setup_title": "Configuracion de Experimento 2",
        "implemented": True,
        "total_trials_multiplier": 2,
    },
    "motor_observation": {
        "code": "MO",
        "slug": "mo",
        "label": "Motor Observation",
        "menu_label": "Experimento 3",
        "setup_title": "Configuracion de Experimento 3",
        "implemented": True,
        "total_trials_multiplier": 2,
    },
    "mix": {
        "code": "MX",
        "slug": "mix",
        "label": "MI + AW + MO",
        "menu_label": "Experimento 4",
        "setup_title": "Configuracion de Experimento 4",
        "implemented": True,
        "total_trials_multiplier": 6,
    },
}

MENU_PROTOCOL_KEYS = [
    "motor_imagery",
    "action_words",
    "motor_observation",
    "mix",
]


def get_protocol_config(protocol_key):
    if protocol_key not in PROTOCOLS:
        raise ValueError(f"Protocolo no soportado: {protocol_key}")

    return PROTOCOLS[protocol_key]


def get_target_config(target_key):
    if target_key not in TARGETS:
        raise ValueError(f"Objetivo no soportado: {target_key}")

    return TARGETS[target_key]


def get_stimulus_gender_config(gender_key):
    if gender_key not in STIMULUS_GENDERS:
        raise ValueError(f"Genero de estimulos no soportado: {gender_key}")

    return STIMULUS_GENDERS[gender_key]
