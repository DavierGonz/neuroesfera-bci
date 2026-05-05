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
        stream_summary = getattr(self.recorder, "stream_summary", {})

        return {
            "backend": getattr(self.recorder, "backend_name", "unknown"),
            "recording_path": getattr(self.recorder, "filename", "unknown"),
            "target_name": self.session_config.target_name,
            "stimulus_gender": self.session_config.stimulus_gender,
            "subject_number": self.session_config.subject_number,
            "session_number": self.session_config.session_number,
            "stream_name": stream_summary.get("stream_name", "unknown"),
            "stream_type": stream_summary.get("stream_type", "unknown"),
            "channel_count": stream_summary.get("channel_count", 0),
            "channel_labels": stream_summary.get("channel_labels", []),
        }
