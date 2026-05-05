# NeuroEsfera BCI Architecture

## Overview

This project now uses a modular architecture with four clear responsibilities:

- `main.py` as bootstrap only
- `core/` for app state and config
- `gui/` for shared visual theme values
- `experiments/` for protocol logic
- `services/` for session orchestration and recording backends
- `eeg/` for LSL marker handling and stream metadata

The application now runs through `PsychoPy` for stimulus presentation and interaction, while recording is handled through a session service that writes XDF through LabRecorder.

## Main Components

### Bootstrap

File:

- `main.py`

Responsibilities:

- create the PsychoPy window
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
- recording defaults
- target selection: Arm vs Leg or Left vs Right
- stimulus gender selection for Motor Observation videos
- automatic session numbering from existing dataset folders

### GUI

Files:

- `core/app_controller.py`
- `gui/ui_theme.py`

Responsibilities:

- draw menu, setup, ready and complete screens with PsychoPy
- map mouse and keyboard input to app transitions
- centralize shared colors and UI constants

### Experiments

Files:

- `experiments/movement_protocols.py`
- `experiments/motor_imagery.py`
- `experiments/action_words.py`
- `experiments/motor_observation.py`
- `experiments/mixed_protocol.py`

Responsibilities:

- define each protocol timeline
- present stimuli
- send LSL markers
- consume injected recording dependencies
- share one timing model across MI, AW, MO and mixed trials

### Services

Files:

- `services/experiment_session.py`
- `services/recording_backend.py`

Responsibilities:

- create the marker outlet once per session
- manage session lifecycle
- start XDF recording through LabRecorder

### EEG / LSL

Files:

- `eeg/lsl_markers.py`
- `eeg/stream_metadata.py`

Responsibilities:

- expose the marker stream
- send marker events
- resolve channel names from stream metadata
- use known electrode labels as fallback defaults for display

## Runtime Flow

1. `main.py` creates the PsychoPy application controller.
2. `AppController` starts in `AppState.MENU`.
3. The user chooses a target (`Arm vs Leg` or `Left vs Right`) and a protocol.
4. `ExperimentSession` creates:
   - one LSL marker outlet
   - one XDF recording backend
5. The XDF backend requires LabRecorder and records the visible LSL streams.
6. The experiment emits markers and advances through baseline, cue, cross and intertrial stages using PsychoPy visual/audio stimuli.
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

### Dataset folders

```text
dataset/<target>/<protocol>/<stimulus_gender>/<subject>/
```

Examples:

- `dataset/arm_vs_leg/mi/hombre/1/`
- `dataset/arm_vs_leg/aw/mujer/2/`
- `dataset/left_vs_right/mo/hombre/3/`
- `dataset/left_vs_right/mix/mujer/4/`

File names use the uppercase format:

```text
AW-LR-H-SUJETO01-SESION01-10-030526.xdf
```

## Recording Notes

- XDF is the recording format used by the project.
- The project uses LabRecorder for XDF because that is the standard LSL recording path.
- Trial timing can be audited with `tests/verify_xdf_timing.py`, which reads marker timestamps from the XDF and compares them against the expected `3 s`, `1.5 s`, `5 s`, `1.5 s` sequence.
- If the EEG stream does not expose channel labels, the project fallback mapping is:
  - `Canal 1 -> Fz`
  - `Canal 2 -> C3`
  - `Canal 3 -> Cz`
  - `Canal 4 -> C4`
  - `Canal 5 -> Pz`
  - `Canal 6 -> PO7`
  - `Canal 7 -> Oz`
  - `Canal 8 -> PO8`

## Current Strengths

- `main.py` is now small and focused.
- Session creation is centralized.
- Experiments receive dependencies instead of creating them.
- XDF recording is integrated directly through LabRecorder.
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
|   `-- motor_observation/
|       |-- arm_vs_leg/
|       |   |-- hombre/
|       |   `-- mujer/
|       `-- left_vs_right/
|-- tests/
|-- main.py
`-- requirements.txt
```

## Project Materials

- `stimuli/motor_observation/`: videos used by Motor Observation during the experiment.
- `docs/source_materials/`: design documents, condition spreadsheets and reference files that are not loaded directly by the app.
