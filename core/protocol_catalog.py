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


LM_BLOCKS = {
    "block_1": {
        "label": "Bloque 1 - Sin tSCS",
        "folder": "Bloque 1 - Sin tSCS",
    },
    "block_2": {
        "label": "Bloque 2 - Con tSCS",
        "folder": "Bloque 2 - Con tSCS",
    },
    "block_3": {
        "label": "Bloque 3 - Medicion de MEP",
        "folder": "Bloque 3 - Medicion de MEP",
    },
}

LM_BLOCK_KEYS = ["block_1", "block_2", "block_3"]


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
        "dataset_slug": "experimento_1",
        "target_key": "left_vs_right",
        "modalities": ["MI"],
        "class_keys": ["left", "right"],
        "total_trials_multiplier": 2,
    },
    "action_words": {
        "code": "AW",
        "slug": "aw",
        "label": "Action Words",
        "menu_label": "Experimento 2",
        "setup_title": "Configuracion de Experimento 2",
        "implemented": True,
        "dataset_slug": "experimento_2",
        "target_key": "arm_vs_leg",
        "modalities": ["MI", "MO", "AW"],
        "class_keys": ["arm", "leg"],
        "total_trials_multiplier": 6,
    },
    "lm": {
        "code": "LM",
        "slug": "lm",
        "label": "LM",
        "menu_label": "Experimento 3",
        "setup_title": "Configuracion de Experimento 3",
        "implemented": True,
        "dataset_slug": "experimento_3",
        "target_key": "arm_vs_leg",
        "modalities": ["MI", "MO", "AW", "ME"],
        "class_keys": ["arm", "leg"],
        "blocks": LM_BLOCKS,
        "default_block_key": "block_1",
        "trials_per_modality": 10,
        "total_trials": 40,
    },
}

MENU_PROTOCOL_KEYS = [
    "motor_imagery",
    "action_words",
    "lm",
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


def get_lm_block_config(block_key):
    if block_key not in LM_BLOCKS:
        raise ValueError(f"Bloque LM no soportado: {block_key}")

    return LM_BLOCKS[block_key]
