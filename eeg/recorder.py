from pylsl import StreamInlet, resolve_streams
import csv
import time
import os

from core.config import DATA_DIR
from eeg.stream_metadata import build_stream_summary


class EEGRecorder:

    def __init__(self, output_path=None):

        print("Buscando streams LSL...")

        eeg_stream = None
        marker_stream = None

        # Esperar hasta que aparezcan los streams
        while eeg_stream is None or marker_stream is None:

            streams = resolve_streams()

            for s in streams:

                if s.type() in {"Data", "EEG"}:
                    eeg_stream = s

                if s.type() == "Markers":
                    marker_stream = s

            if eeg_stream is None or marker_stream is None:
                print("Esperando streams...")
                time.sleep(1)

        print("EEG stream encontrado:", eeg_stream.name())
        print("Marker stream encontrado")

        self.eeg_inlet = StreamInlet(eeg_stream)
        self.marker_inlet = StreamInlet(marker_stream)
        self.stream_summary = build_stream_summary(eeg_stream)

        self.current_marker = ""
        self.current_trial = 0
        self.channel_labels = self.stream_summary["channel_labels"]

        os.makedirs(DATA_DIR, exist_ok=True)

        if output_path is None:
            timestamp = int(time.time())
            output_path = os.path.join(DATA_DIR, f"session_{timestamp}.csv")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.filename = output_path

        self.file = open(self.filename, "w", newline="")
        self.writer = csv.writer(self.file)

        self.writer.writerow([
            "timestamp",
            *self.channel_labels,
            "trial",
            "marker"
        ])

        print("Grabando dataset en:", self.filename)

    # ---------------------------------------

    def update_marker(self):

        marker, ts = self.marker_inlet.pull_sample(timeout=0)

        if marker:

            marker = marker[0]

            print("Marker recibido:", marker)

            self.current_marker = marker

            if marker.startswith("TRIAL_"):
                try:
                    self.current_trial = int(marker.split("_")[1])
                except:
                    pass

    # ---------------------------------------

    def record_sample(self):

        sample, timestamp = self.eeg_inlet.pull_sample(timeout=1)

        if sample:

            row = (
                [timestamp]
                + sample[:8]
                + [self.current_trial]
                + [self.current_marker]
            )

            self.writer.writerow(row)

    def record_for_duration(self, duration, poll_interval=0.004, on_tick=None):

        start = time.time()

        while time.time() - start < duration:

            self.update_marker()
            self.record_sample()

            if on_tick is not None:
                on_tick()

            time.sleep(poll_interval)

    # ---------------------------------------

    def close(self):

        self.file.close()

        print("Dataset guardado:", self.filename)
