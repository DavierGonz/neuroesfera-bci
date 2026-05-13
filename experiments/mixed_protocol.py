from experiments.movement_protocols import run_protocol_by_key


def run_experiment_2(window, trials, marker_outlet, recorder, stimulus_gender):
    run_protocol_by_key(
        window,
        trials,
        marker_outlet,
        recorder,
        stimulus_gender,
        "experiment_2",
    )


def run_experiment_3(window, trials, marker_outlet, recorder, stimulus_gender):
    run_protocol_by_key(
        window,
        trials,
        marker_outlet,
        recorder,
        stimulus_gender,
        "experiment_3",
    )
