import os
import json

from eeg.lsl_markers import create_marker_stream
from services.recording_backend import create_recording_backend


class ExperimentSession:
    def __init__(self, session_config):
        self.session_config = session_config
        self.marker_outlet = create_marker_stream()
        self.recorder = create_recording_backend(session_config)
        self.session_result = None

    def close(self):
        self.recorder.close()
        self.session_result = self._load_session_result()

    def _load_session_result(self):
        summary_path = getattr(self.recorder, "summary_path", None)

        if summary_path and os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as summary_file:
                return json.load(summary_file)

        return {
            "backend": getattr(self.recorder, "backend_name", "unknown"),
            "recording_path": getattr(self.recorder, "filename", "unknown"),
            "stream_name": "unknown",
            "stream_type": "unknown",
            "channel_labels": [],
        }
