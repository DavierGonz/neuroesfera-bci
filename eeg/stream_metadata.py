import time

from pylsl import resolve_streams

from core.config import DEFAULT_EEG_CHANNEL_LABELS


def default_channel_names(channel_count, prefix="EEG"):
    count = max(int(channel_count or 0), 0)

    # When the stream does not publish channel labels, use the project mapping
    # for EEG channels 1..8 so the UI and notebook stay consistent.
    if prefix == "EEG" and count <= len(DEFAULT_EEG_CHANNEL_LABELS):
        return DEFAULT_EEG_CHANNEL_LABELS[:count]

    return [f"{prefix}{index}" for index in range(1, count + 1)]


def resolve_eeg_stream_info(timeout=15, poll_interval=1.0):
    deadline = time.time() + timeout

    while time.time() < deadline:
        candidates = [
            stream
            for stream in resolve_streams()
            if stream.type() in {"Data", "EEG"}
        ]
        if candidates:
            return sorted(candidates, key=_stream_priority)[0]

        time.sleep(poll_interval)

    return None


def _stream_priority(stream):
    stream_type = stream.type()
    stream_name = stream.name().upper()
    channel_count = stream.channel_count()

    if stream_type == "EEG":
        return (0, abs(channel_count - 8), stream_name)

    if stream_name.endswith("_EEG"):
        return (1, abs(channel_count - 8), stream_name)

    return (2, abs(channel_count - 8), stream_name)


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

    return []


def build_stream_summary(stream_info):
    if stream_info is None:
        return {
            "stream_name": "unknown",
            "stream_type": "unknown",
            "channel_count": 0,
            "channel_labels": extract_channel_labels(None),
        }

    return {
        "stream_name": stream_info.name(),
        "stream_type": stream_info.type(),
        "channel_count": stream_info.channel_count(),
        "channel_labels": extract_channel_labels(stream_info),
    }
