from pylsl import StreamInlet, resolve_streams
import csv
import time
import os


class EEGRecorder:

    def __init__(self):

        print("Buscando streams LSL...")

        eeg_stream = None
        marker_stream = None

        # Esperar hasta que aparezcan los streams
        while eeg_stream is None or marker_stream is None:

            streams = resolve_streams()

            for s in streams:

                if s.type() == "Data":
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

        self.current_marker = ""
        self.current_trial = 0

        os.makedirs("data", exist_ok=True)

        timestamp = int(time.time())
        self.filename = f"data/session_{timestamp}.csv"

        self.file = open(self.filename, "w", newline="")
        self.writer = csv.writer(self.file)

        self.writer.writerow([
            "timestamp",
            "ch1","ch2","ch3","ch4",
            "ch5","ch6","ch7","ch8",
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

    # ---------------------------------------

    def close(self):

        self.file.close()

        print("Dataset guardado:", self.filename)