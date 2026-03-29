import time

from pylsl import resolve_streams

from core.config import DEFAULT_EEG_CHANNEL_LABELS


def resolve_eeg_stream_info(timeout=15, poll_interval=1.0):
    deadline = time.time() + timeout

    while time.time() < deadline:
        for stream in resolve_streams():
            if stream.type() in {"Data", "EEG"}:
                return stream

        time.sleep(poll_interval)

    return None


def extract_channel_labels(stream_info, limit=8):
    labels = []

    if stream_info is not None:
        try:
            channels = stream_info.desc().child("channels")
            channel = channels.child("channel")

            while channel.name():
                label = channel.child_value("label") or channel.child_value("name")

                if label:
                    labels.append(label)

                channel = channel.next_sibling("channel")
        except Exception:
            labels = []

    if labels:
        return labels[:limit]

    fallback = DEFAULT_EEG_CHANNEL_LABELS[:limit]

    if len(fallback) < limit:
        fallback = fallback + [
            f"ch{i}"
            for i in range(len(fallback) + 1, limit + 1)
        ]

    return fallback


def build_stream_summary(stream_info):
    if stream_info is None:
        return {
            "stream_name": "unknown",
            "stream_type": "unknown",
            "channel_labels": extract_channel_labels(None),
        }

    return {
        "stream_name": stream_info.name(),
        "stream_type": stream_info.type(),
        "channel_labels": extract_channel_labels(stream_info),
    }
