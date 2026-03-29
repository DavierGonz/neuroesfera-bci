# NeuroEsfera BCI Architecture

## Overview

This project now uses a modular architecture with four clear responsibilities:

- `main.py` as bootstrap only
- `core/` for app state and config
- `gui/` for presentation
- `experiments/` for protocol logic
- `services/` for session orchestration and recording backends
- `eeg/` for LSL marker handling and CSV fallback recording

The application is event-driven through `pygame`, while recording is handled through a session service that prefers XDF through LabRecorder and falls back to CSV when XDF is not available.

## Main Components

### Bootstrap

File:

- `main.py`

Responsibilities:

- initialize `pygame`
- create the window
- load config values
- start the application controller

### Core

Files:

- `core/app_controller.py`
- `core/state_manager.py`
- `core/config.py`

Responsibilities:

- application flow
- app states
- window settings
- recording backend selection
- recording defaults

### GUI

Files:

- `gui/menu.py`
- `gui/motor_imagery_setup.py`

Responsibilities:

- draw screens
- map user interaction to app transitions

### Experiments

Files:

- `experiments/motor_imagery.py`

Responsibilities:

- define each protocol timeline
- present stimuli
- send LSL markers
- consume injected recording dependencies

### Services

Files:

- `services/experiment_session.py`
- `services/recording_backend.py`

Responsibilities:

- create the marker outlet once per session
- select the recording backend
- manage session lifecycle
- start XDF recording through LabRecorder when available
- fall back to CSV recording when XDF is unavailable

### EEG / LSL

Files:

- `eeg/lsl_markers.py`
- `eeg/recorder.py`
- `eeg/stream_metadata.py`

Responsibilities:

- expose the marker stream
- send marker events
- read EEG + markers for CSV fallback
- resolve channel names from stream metadata
- use known electrode labels as fallback defaults

## Runtime Flow

1. `main.py` initializes `pygame` and creates the window.
2. `AppController` starts in `AppState.MENU`.
3. The user chooses an experiment from the GUI.
4. `ExperimentSession` creates:
   - one LSL marker outlet
   - one recording backend
5. The backend selection works like this:
   - if `RECORDING_BACKEND` is `xdf`, it requires LabRecorder
   - if `RECORDING_BACKEND` is `csv`, it records through `EEGRecorder`
   - if `RECORDING_BACKEND` is `auto`, it prefers XDF and falls back to CSV
6. The experiment emits markers and advances through its stages.
7. The recording backend keeps the session alive for each stage duration.
8. At the end of the experiment, the session is closed and the app returns to the menu.

## Data Flow

### XDF path

```text
Experiment
-> LSL markers
-> LabRecorder
-> .xdf file

External EEG stream
-> LabRecorder
-> .xdf file
```

### CSV fallback path

```text
Experiment
-> LSL markers
-> EEGRecorder
-> .csv file

External EEG stream
-> EEGRecorder
-> .csv file
```

## Recording Notes

- XDF is the preferred format because it preserves full LSL stream structure.
- The project uses LabRecorder for XDF because that is the standard LSL recording path.
- If LabRecorder is not installed or not reachable, the project can still record CSV in `auto` mode.
- CSV headers now use electrode names from the stream metadata when available.
- If the EEG stream does not expose channel labels, the fallback names are:
  - `Fz`, `C3`, `Cz`, `C4`, `Pz`, `PO7`, `Oz`, `PO8`

## Current Strengths

- `main.py` is now small and focused.
- Session creation is centralized.
- Experiments receive dependencies instead of creating them.
- XDF support is integrated without removing a safe CSV fallback.
- Dead UI options and unused helper modules have been removed.

## Current Structure

```text
BCI/
|-- core/
|-- dataset/
|-- docs/
|-- eeg/
|-- experiments/
|-- gui/
|-- services/
|-- stimuli/
|-- tests/
|-- main.py
`-- requirements.txt
```
