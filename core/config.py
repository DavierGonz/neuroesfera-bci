WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
WINDOW_TITLE = "NeuroEsfera BCI"
FULLSCREEN = True

DATA_DIR = "dataset"

# Recording backend options: "auto", "xdf", "csv"
RECORDING_BACKEND = "auto"

LABRECORDER_PATH = r"C:\LSL\LabRecorder\LabRecorder.exe"
UNICORN_LSL_PATH = (
    r"C:\Users\Usuario\Documents\gtec\Unicorn Suite\Hybrid Black\Unicorn LSL\UnicornLSL.exe"
)
LABRECORDER_RCS_HOST = "127.0.0.1"
LABRECORDER_RCS_PORT = 22345
LABRECORDER_STARTUP_TIMEOUT = 15
LABRECORDER_SETTLE_SECONDS = 1.0

DEFAULT_EEG_CHANNEL_LABELS = [
    "Fz",
    "C3",
    "Cz",
    "C4",
    "Pz",
    "PO7",
    "Oz",
    "PO8",
]
