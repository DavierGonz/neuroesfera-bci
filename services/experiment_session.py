from eeg.lsl_markers import create_marker_stream
from services.recording_backend import create_recording_backend
from time import perf_counter, sleep


class ExperimentSession:
    def __init__(self, session_config, preview_mode=False):
        self.session_config = session_config
        self.preview_mode = preview_mode
        if preview_mode:
            self.marker_outlet = PreviewMarkerOutlet()
            self.recorder = PreviewRecordingBackend(session_config)
        else:
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


class PreviewMarkerOutlet:
    def push_sample(self, sample):
        print("Preview marker:", sample[0] if sample else "")


class PreviewRecordingBackend:
    def __init__(self, session_config):
        self.filename = f"PREVIEW-{session_config.build_basename()}.xdf"
        self.backend_name = "preview"
        self.stream_summary = {
            "stream_name": "preview-no-lsl",
            "stream_type": "preview",
            "channel_count": 0,
            "channel_labels": [],
        }
        print("Modo preview: no se abre LabRecorder ni se requiere casco.")

    def record_for_duration(self, duration, poll_interval=0.004, on_tick=None):
        start = perf_counter()

        while perf_counter() - start < duration:
            if on_tick is not None:
                on_tick()

            sleep(poll_interval)

    def close(self):
        print("Preview finalizado: no se genero archivo XDF.")
