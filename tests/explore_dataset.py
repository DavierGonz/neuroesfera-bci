import csv
import json
from pathlib import Path


DATASET_DIR = Path('dataset')


def main():
    if not DATASET_DIR.exists():
        print('No existe la carpeta dataset.')
        return

    files = sorted(
        [path for path in DATASET_DIR.rglob('*') if path.is_file()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not files:
        print('No hay archivos dentro de dataset.')
        return

    print('Archivos encontrados en dataset:')
    for path in files:
        print(f'- {path} | {path.stat().st_size} bytes')

    summary_files = [path for path in files if path.name.endswith('_summary.json')]

    if not summary_files:
        print('\nNo hay archivos summary para inspeccionar.')
        return

    latest = summary_files[0]
    payload = load_summary(latest)

    print(f'\nUltimo summary detectado: {latest}')
    print('\nResumen de sesion:')
    print(f"- Backend: {payload.get('backend', 'unknown')}")
    print(f"- Archivo: {payload.get('recording_path', 'unknown')}")
    print(f"- Stream EEG: {payload.get('stream_name', 'unknown')}")
    print(f"- Tipo stream: {payload.get('stream_type', 'unknown')}")
    print(f"- Electrodos: {', '.join(payload.get('channel_labels', []))}")

    recording_path = Path(payload.get('recording_path', ''))
    if not recording_path.exists():
        print('\nNo se encontro el archivo principal de grabacion.')
        return

    print('\nFlujo detectado:')
    if recording_path.suffix.lower() == '.csv':
        trial_flow = extract_trial_flow_from_csv(recording_path)
        print_trial_flow(trial_flow)
        return

    if recording_path.suffix.lower() == '.xdf':
        try:
            import pyxdf
        except ImportError:
            print('No tienes pyxdf instalado.')
            print('Instala con: pip install pyxdf')
            print('Luego vuelve a ejecutar este script o usa el notebook.')
            return

        trial_flow = extract_trial_flow_from_xdf(recording_path, pyxdf)
        print_trial_flow(trial_flow)
        return

    print(f'No hay lector implementado para {recording_path.suffix}.')


def load_summary(summary_path):
    with summary_path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def extract_trial_flow_from_csv(csv_path):
    flow = []
    seen_trials = set()

    with csv_path.open('r', encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            trial = row.get('trial', '').strip()
            marker = row.get('marker', '').strip()

            if not trial or not marker.startswith('MI_'):
                continue

            key = (int(trial), marker)
            if key in seen_trials:
                continue

            seen_trials.add(key)
            flow.append(key)

    return sorted(flow, key=lambda item: item[0])


def extract_trial_flow_from_xdf(xdf_path, pyxdf):
    streams, _ = pyxdf.load_xdf(str(xdf_path))
    marker_stream = None

    for stream in streams:
        stream_type = stream['info']['type'][0]
        if stream_type == 'Markers':
            marker_stream = stream
            break

    if marker_stream is None:
        return []

    markers = []
    for sample in marker_stream['time_series']:
        if not sample:
            continue
        markers.append(str(sample[0]))

    flow = []
    current_trial = None
    pending_motor_marker = None

    for marker in markers:
        if marker.startswith('TRIAL_'):
            try:
                current_trial = int(marker.split('_')[1])
            except ValueError:
                current_trial = None

            if pending_motor_marker is not None and current_trial is not None:
                flow.append((current_trial, pending_motor_marker))
                pending_motor_marker = None
            continue

        if not marker.startswith('MI_'):
            continue

        if current_trial is not None:
            flow.append((current_trial, marker))
            current_trial = None
        else:
            pending_motor_marker = marker

    deduped = []
    seen = set()
    for item in flow:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)

    return sorted(deduped, key=lambda item: item[0])


def print_trial_flow(trial_flow):
    if not trial_flow:
        print('- No se detecto flujo de trials.')
        return

    for trial, marker in trial_flow:
        print(f'- Trial {trial}: {marker}')


if __name__ == '__main__':
    main()
