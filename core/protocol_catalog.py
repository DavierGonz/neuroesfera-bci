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

EXPERIMENT_3_BLOCKS = {
    "bloque1": {
        "code": "B1",
        "label": "Bloque 1 - Sin tSCS",
        "folder": "bloque1",
    },
    "bloque2": {
        "code": "B2",
        "label": "Bloque 2 - Con tSCS",
        "folder": "bloque2",
    },
    "bloque3": {
        "code": "B3",
        "label": "Bloque 3 - Medicion de MEP",
        "folder": "bloque3",
    },
}

EXPERIMENT_3_BLOCK_KEYS = ["bloque1", "bloque2", "bloque3"]


PROTOCOLS = {
    "experiment_1": {
        "code": "MI",
        "slug": "mi",
        "label": "Experimento 1 - MI",
        "menu_label": "Experimento 1",
        "setup_title": "Configuracion de Experimento 1",
        "implemented": True,
        "dataset_slug": "experimento_1",
        "target_key": "arm_vs_leg",
        "modalities": ["MI"],
        "class_keys": ["arm", "leg"],
        "total_trials_multiplier": 2,
    },
    "experiment_2": {
        "code": "MI-MO-AW",
        "slug": "mi_mo_aw",
        "label": "Experimento 2 - MI + MO + AW",
        "menu_label": "Experimento 2",
        "setup_title": "Configuracion de Experimento 2",
        "implemented": True,
        "dataset_slug": "experimento_2",
        "target_key": "arm_vs_leg",
        "modalities": ["MI", "MO", "AW"],
        "class_keys": ["arm", "leg"],
        "trials_per_modality": 10,
        "total_trials": 30,
    },
    "experiment_3": {
        "code": "MI",
        "slug": "mi_mo_aw_me",
        "label": "Experimento 3 - MI + MO + AW + ME",
        "menu_label": "Experimento 3",
        "setup_title": "Configuracion de Experimento 3",
        "implemented": True,
        "dataset_slug": "experimento_3",
        "target_key": "arm_vs_leg",
        "modalities": ["MI", "MO", "AW", "ME"],
        "class_keys": ["arm", "leg"],
        "trials_per_modality": 10,
        "total_trials": 40,
        "block_options": EXPERIMENT_3_BLOCKS,
        "block_keys": EXPERIMENT_3_BLOCK_KEYS,
        "requires_block": True,
    },
    "paradigm_mi": {
        "code": "MI",
        "slug": "mi",
        "label": "MI",
        "menu_label": "1. MI",
        "setup_title": "Configuracion de Paradigma MI",
        "implemented": True,
        "dataset_slug": "paradigmas/mi",
        "target_key": "arm_vs_leg",
        "modalities": ["MI"],
        "class_keys": ["arm", "leg"],
        "total_trials_multiplier": 2,
    },
    "paradigm_me": {
        "code": "ME",
        "slug": "me",
        "label": "ME",
        "menu_label": "2. ME",
        "setup_title": "Configuracion de Paradigma ME",
        "implemented": True,
        "dataset_slug": "paradigmas/me",
        "target_key": "arm_vs_leg",
        "modalities": ["ME"],
        "class_keys": ["arm", "leg"],
        "total_trials_multiplier": 2,
    },
    "paradigm_mo": {
        "code": "MO",
        "slug": "mo",
        "label": "MO",
        "menu_label": "3. MO",
        "setup_title": "Configuracion de Paradigma MO",
        "implemented": True,
        "dataset_slug": "paradigmas/mo",
        "target_key": "arm_vs_leg",
        "modalities": ["MO"],
        "class_keys": ["arm", "leg"],
        "total_trials_multiplier": 2,
    },
    "paradigm_aw": {
        "code": "AW",
        "slug": "aw",
        "label": "AW",
        "menu_label": "4. AW",
        "setup_title": "Configuracion de Paradigma AW",
        "implemented": True,
        "dataset_slug": "paradigmas/aw",
        "target_key": "arm_vs_leg",
        "modalities": ["AW"],
        "class_keys": ["arm", "leg"],
        "total_trials_multiplier": 2,
    },
}

MAIN_EXPERIMENT_KEYS = [
    "experiment_1",
    "experiment_2",
    "experiment_3",
]

PARADIGM_PROTOCOL_KEYS = [
    "paradigm_mi",
    "paradigm_me",
    "paradigm_mo",
    "paradigm_aw",
]

MENU_PROTOCOL_KEYS = MAIN_EXPERIMENT_KEYS


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


def get_block_config(block_key):
    if block_key not in EXPERIMENT_3_BLOCKS:
        raise ValueError(f"Bloque no soportado: {block_key}")

    return EXPERIMENT_3_BLOCKS[block_key]
