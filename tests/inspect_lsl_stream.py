import argparse
import time

from pylsl import StreamInlet, resolve_streams


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Inspecciona streams LSL en vivo y muestra metadata de canales, "
            "estructura desc y una muestra opcional."
        )
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="Segundos maximos para esperar a que aparezcan streams.",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Intervalo de sondeo mientras se esperan streams.",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Nombre exacto del stream a inspeccionar. Ej: UN-2019.06.47",
    )
    parser.add_argument(
        "--type",
        type=str,
        default=None,
        help="Tipo exacto del stream a inspeccionar. Ej: Data, EEG o Markers",
    )
    parser.add_argument(
        "--sample-timeout",
        type=float,
        default=2.0,
        help="Tiempo maximo para leer una muestra del stream seleccionado.",
    )
    parser.add_argument(
        "--no-sample",
        action="store_true",
        help="No intenta leer una muestra; solo imprime metadata.",
    )
    return parser.parse_args()


def resolve_available_streams(timeout, poll_interval):
    deadline = time.time() + timeout

    while time.time() < deadline:
        streams = resolve_streams()
        if streams:
            return streams
        time.sleep(poll_interval)

    return []


def first_value(value):
    if isinstance(value, list):
        return value[0] if value else ""
    if value is None:
        return ""
    return value


def extract_channel_labels(stream):
    labels = []

    try:
        channels = stream.desc().child("channels")
        channel = channels.child("channel")

        while channel.name():
            label = channel.child_value("label") or channel.child_value("name")
            if label:
                labels.append(label)
            channel = channel.next_sibling("channel")
    except Exception as error:
        return [], f"no se pudo leer desc/channels: {error}"

    if labels:
        return labels, None

    return [], "desc/channels vacio o sin labels/name"


def extract_desc_tree(node, depth=0, max_depth=4):
    lines = []

    if depth >= max_depth:
        return lines

    try:
        child = node.first_child()
    except Exception:
        return lines

    while child is not None and child.name():
        indent = "  " * depth
        value = child.value()
        suffix = f": {value}" if value else ""
        lines.append(f"{indent}- {child.name()}{suffix}")
        lines.extend(extract_desc_tree(child, depth + 1, max_depth=max_depth))
        child = child.next_sibling()

    return lines


def print_stream_summary(streams):
    print(f"Streams encontrados: {len(streams)}")
    print("")

    for index, stream in enumerate(streams):
        print(f"[{index}] nombre={stream.name()} | tipo={stream.type()} | canales={stream.channel_count()}")

    print("")


def stream_priority(stream):
    stream_type = stream.type()
    stream_name = stream.name().upper()
    channel_count = stream.channel_count()

    if stream_type == "EEG":
        return (0, abs(channel_count - 8), stream_name)

    if stream_name.endswith("_EEG"):
        return (1, abs(channel_count - 8), stream_name)

    if stream_type == "Data":
        return (2, abs(channel_count - 8), stream_name)

    return (3, abs(channel_count - 8), stream_name)


def select_stream(streams, name=None, stream_type=None):
    matches = []

    for stream in streams:
        if name is not None and stream.name() != name:
            continue
        if stream_type is not None and stream.type() != stream_type:
            continue
        matches.append(stream)

    if name is None and stream_type is None:
        if not streams:
            return None
        return sorted(streams, key=stream_priority)[0]

    if not matches:
        return None

    return matches[0]


def inspect_stream(stream, sample_timeout, read_sample=True):
    print("Stream seleccionado")
    print("-------------------")
    print("nombre:", stream.name())
    print("tipo:", stream.type())
    print("source_id:", stream.source_id())
    print("uid:", stream.uid())
    print("hostname:", stream.hostname())
    print("canales:", stream.channel_count())
    print("nominal_srate:", stream.nominal_srate())
    print("channel_format:", stream.channel_format())
    print("")

    labels, label_error = extract_channel_labels(stream)
    if labels:
        print("Labels detectados:")
        for index, label in enumerate(labels):
            print(f"  ch{index + 1}: {label}")
    else:
        print("Labels detectados: ninguno")
        if label_error:
            print("Motivo:", label_error)

    print("")
    print("Arbol desc (si existe):")
    desc_lines = extract_desc_tree(stream.desc())
    if desc_lines:
        for line in desc_lines:
            print(line)
    else:
        print("  sin metadata adicional en desc")

    if not read_sample:
        return

    print("")
    print("Leyendo una muestra...")
    inlet = StreamInlet(stream)
    sample, timestamp = inlet.pull_sample(timeout=sample_timeout)

    if sample is None:
        print("No se pudo leer una muestra dentro del timeout.")
        return

    print("timestamp:", timestamp)
    print("longitud muestra:", len(sample))
    preview = sample[: min(10, len(sample))]
    print("primeros valores:", preview)


def main():
    args = parse_args()
    streams = resolve_available_streams(args.timeout, args.poll_interval)

    if not streams:
        print("No se encontraron streams LSL dentro del tiempo esperado.")
        print("")
        print("Sugerencia:")
        print("- Enciende el casco")
        print("- Abre UnicornLSL")
        print("- Pulsa Open y luego Start")
        print("- Repite este script")
        return

    print_stream_summary(streams)

    stream = select_stream(streams, name=args.name, stream_type=args.type)
    if stream is None:
        print("No hubo coincidencia con los filtros solicitados.")
        print(f"name={args.name!r}, type={args.type!r}")
        return

    if args.name is None and args.type is None:
        print(
            "Seleccion automatica: "
            f"se priorizo '{stream.name()}' por tipo/canal para inspeccion BCI."
        )
        print("")

    inspect_stream(
        stream,
        sample_timeout=args.sample_timeout,
        read_sample=not args.no_sample,
    )


if __name__ == "__main__":
    main()
