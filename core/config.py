WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
WINDOW_TITLE = "NeuroEsfera BCI"
FULLSCREEN = True

DATA_DIR = "dataset"

LABRECORDER_PATH = r"C:\LSL\LabRecorder\LabRecorder.exe"
UNICORN_LSL_PATH = (
    r"C:\Users\Usuario\Documents\gtec\Unicorn Suite\Hybrid Black\Unicorn LSL\UnicornLSL.exe"
)
LABRECORDER_RCS_HOST = "127.0.0.1"
LABRECORDER_RCS_PORT = 22345
LABRECORDER_STARTUP_TIMEOUT = 15
LABRECORDER_SETTLE_SECONDS = 1.0

# Project-level fallback mapping used when UnicornLSL / XDF does not expose
# real channel labels in stream metadata.
DEFAULT_EEG_CHANNEL_MAPPING = {
    1: "Fz",
    2: "C3",
    3: "Cz",
    4: "C4",
    5: "Pz",
    6: "PO7",
    7: "Oz",
    8: "PO8",
}

DEFAULT_EEG_CHANNEL_LABELS = list(DEFAULT_EEG_CHANNEL_MAPPING.values())
