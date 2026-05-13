import argparse
from pathlib import Path

import pyxdf

from experiments.trial_sequences import TRIAL_SEQUENCES


EXPERIMENT_BY_FILE_PREFIX = {
    "MI-MO-AW": "experiment_2",
    "MI": "experiment_1",
    "ME": "paradigm_me",
    "MO": "paradigm_mo",
    "AW": "paradigm_aw",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Verifica duraciones de trials usando timestamps de markers en un XDF."
    )
    parser.add_argument(
        "xdf",
        nargs="?",
        help="Ruta del XDF. Si se omite, usa el XDF mas reciente en dataset/.",
    )
    parser.add_argument(
        "--experiment",
        choices=sorted(TRIAL_SEQUENCES.keys()),
        default=None,
        help="Secuencia a usar. Si se omite, se infiere del nombre del XDF.",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.20,
        help="Error maximo permitido por intervalo, en segundos.",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Solo imprime el reporte, sin retornar error si excede la tolerancia.",
    )
    return parser.parse_args()


def find_latest_xdf():
    xdf_files = [path for path in Path("dataset").rglob("*.xdf") if path.is_file()]
    if not xdf_files:
        raise FileNotFoundError("No se encontraron archivos .xdf en dataset/.")

    return max(xdf_files, key=lambda path: path.stat().st_mtime)


def infer_experiment_key(xdf_path):
    path_parts = {part.lower() for part in xdf_path.parts}
    if "experimento_2" in path_parts:
        return "experiment_2"
    if "experimento_3" in path_parts:
        return "experiment_3"

    filename = xdf_path.name.upper()
    prefix = next(
        (
            candidate
            for candidate in sorted(EXPERIMENT_BY_FILE_PREFIX, key=len, reverse=True)
            if filename.startswith(f"{candidate}-")
        ),
        None,
    )

    if prefix not in EXPERIMENT_BY_FILE_PREFIX:
        raise ValueError(
            "No se pudo inferir el experimento desde el nombre del XDF. "
            "Usa --experiment con una clave disponible en TRIAL_SEQUENCES."
        )

    return EXPERIMENT_BY_FILE_PREFIX[prefix]


def marker_value(sample):
    if isinstance(sample, (list, tuple)):
        return str(sample[0])

    return str(sample)


def load_marker_events(xdf_path):
    streams, _ = pyxdf.load_xdf(str(xdf_path))
    marker_stream = next(
        (
            stream
            for stream in streams
            if stream.get("info", {}).get("type", [""])[0] == "Markers"
        ),
        None,
    )

    if marker_stream is None:
        raise ValueError("El XDF no contiene stream de Markers.")

    return [
        (marker_value(sample), float(timestamp))
        for sample, timestamp in zip(
            marker_stream["time_series"],
            marker_stream["time_stamps"],
        )
    ]


def first_timestamp(segment, marker):
    for value, timestamp in segment:
        if value == marker:
            return timestamp

    return None


def trial_segments(events):
    trial_starts = [
        index
        for index, (marker, _) in enumerate(events)
        if marker.startswith("TRIAL_")
    ]

    for position, start_index in enumerate(trial_starts):
        if position + 1 < len(trial_starts):
            end_index = trial_starts[position + 1]
        else:
            end_index = next(
                (
                    index
                    for index in range(start_index + 1, len(events))
                    if events[index][0] == "END"
                ),
                len(events),
            )

        yield events[start_index:end_index], events[end_index] if end_index < len(events) else None


def expected_intervals(experiment_key):
    sequence = TRIAL_SEQUENCES[experiment_key]
    intervals = []

    for index, stage_config in enumerate(sequence):
        stage_marker, duration = stage_config[:2]
        if index + 1 < len(sequence):
            next_marker = sequence[index + 1][0]
        else:
            next_marker = "NEXT_TRIAL_OR_END"

        intervals.append((f"{stage_marker}_TO_{next_marker}", stage_marker, next_marker, duration))

    return intervals


def measure_trials(events, experiment_key):
    measurements = []
    intervals = expected_intervals(experiment_key)
    required_markers = [stage_marker for _, stage_marker, _, _ in intervals]

    for segment, next_event in trial_segments(events):
        trial_marker = segment[0][0]
        timestamps = {
            marker: first_timestamp(segment, marker)
            for marker in required_markers
        }
        timestamps["NEXT_TRIAL_OR_END"] = next_event[1] if next_event else None

        missing = [
            marker
            for _, stage_marker, next_marker, _ in intervals
            for marker in (stage_marker, next_marker)
            if timestamps.get(marker) is None
        ]

        if missing:
            measurements.append((trial_marker, "MISSING", sorted(set(missing)), None, None))
            continue

        for interval_name, stage_marker, next_marker, expected in intervals:
            actual = timestamps[next_marker] - timestamps[stage_marker]
            measurements.append(
                (
                    trial_marker,
                    interval_name,
                    actual,
                    expected,
                    actual - expected,
                )
            )

    return measurements


def main():
    args = parse_args()
    xdf_path = Path(args.xdf) if args.xdf else find_latest_xdf()
    experiment_key = args.experiment or infer_experiment_key(xdf_path)
    events = load_marker_events(xdf_path)
    measurements = measure_trials(events, experiment_key)
    failures = []

    print("Archivo:", xdf_path)
    print("Experimento:", experiment_key)
    print("Tolerancia:", args.tolerance, "s")
    print("")
    print("trial\tintervalo\treal_s\tesperado_s\terror_s")

    for trial, interval, actual, expected, error in measurements:
        if interval == "MISSING":
            print(f"{trial}\tMISSING\t{','.join(actual)}\t-\t-")
            failures.append((trial, interval, actual))
            continue

        print(f"{trial}\t{interval}\t{actual:.4f}\t{expected:.4f}\t{error:+.4f}")
        if abs(error) > args.tolerance:
            failures.append((trial, interval, error))

    print("")
    if failures:
        print(f"Resultado: {len(failures)} intervalos fuera de tolerancia.")
        if not args.no_fail:
            raise SystemExit(1)
    else:
        print("Resultado: tiempos dentro de tolerancia.")


if __name__ == "__main__":
    main()
