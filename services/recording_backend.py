import os
import shutil
import socket
import subprocess
import tempfile
import time

from core.config import (
    DATA_DIR,
    LABRECORDER_PATH,
    LABRECORDER_RCS_HOST,
    LABRECORDER_RCS_PORT,
    LABRECORDER_SETTLE_SECONDS,
    LABRECORDER_STARTUP_TIMEOUT,
    UNICORN_LSL_PATH,
)
from eeg.stream_metadata import build_stream_summary, resolve_eeg_stream_info


class XDFRecordingBackend:
    def __init__(self, session_config):
        self.filename = _build_output_path(session_config, "xdf")
        self._labrecorder_process = None
        self._rcs_socket = None
        self._temp_config_path = None
        self.backend_name = "xdf"
        self.stream_summary = build_stream_summary(resolve_eeg_stream_info())

        executable = self._find_labrecorder()
        if executable is None:
            raise RuntimeError(self._build_missing_labrecorder_message())

        self._temp_config_path = self._create_temp_config()
        self._labrecorder_process = subprocess.Popen(
            [executable, "-c", self._temp_config_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        self._rcs_socket = self._wait_for_rcs_socket()
        self._send_command("update")
        time.sleep(2.0)
        self._send_command("select all")
        self._send_command(
            "filename "
            f"{{root:{os.path.dirname(self.filename)}}} "
            f"{{template:{os.path.basename(self.filename)}}}"
        )
        self._send_command("start")
        time.sleep(LABRECORDER_SETTLE_SECONDS)

        print("Grabando dataset en:", self.filename)

    def record_for_duration(self, duration, poll_interval=0.004, on_tick=None):
        start = time.time()

        while time.time() - start < duration:
            if on_tick is not None:
                on_tick()

            time.sleep(poll_interval)

    def close(self):
        try:
            if self._rcs_socket:
                self._send_command("stop")
                time.sleep(0.5)
                self._rcs_socket.close()
        finally:
            self._rcs_socket = None

            if self._labrecorder_process:
                self._labrecorder_process.terminate()
                try:
                    self._labrecorder_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._labrecorder_process.kill()

            if self._temp_config_path and os.path.exists(self._temp_config_path):
                os.remove(self._temp_config_path)

            print("Dataset guardado:", self.filename)

    def _find_labrecorder(self):
        candidates = [
            LABRECORDER_PATH,
            shutil.which("LabRecorder"),
            shutil.which("LabRecorder.exe"),
            os.path.join("C:\\", "Program Files", "LabRecorder", "LabRecorder.exe"),
            os.path.join("C:\\", "Program Files", "App-LabRecorder", "LabRecorder.exe"),
        ]

        for candidate in candidates:
            if candidate and os.path.exists(candidate):
                if os.path.basename(candidate).lower() == "unicornlsl.exe":
                    raise RuntimeError(
                        "LABRECORDER_PATH apunta a UnicornLSL.exe. "
                        "Ese programa publica el stream EEG, pero no graba XDF. "
                        "Debes apuntar a LabRecorder.exe."
                    )
                return candidate

        return None

    def _build_missing_labrecorder_message(self):
        message = (
            "No se encontro LabRecorder.exe. "
            "UnicornLSL.exe publica el EEG por LSL, pero no guarda archivos XDF."
        )

        if UNICORN_LSL_PATH and os.path.exists(UNICORN_LSL_PATH):
            message += (
                f" Se detecto UnicornLSL en '{UNICORN_LSL_PATH}', "
                "pero aun falta LabRecorder.exe."
            )

        message += " Instala LabRecorder o configura LABRECORDER_PATH con la ruta de LabRecorder.exe."

        return message

    def _create_temp_config(self):
        fd, path = tempfile.mkstemp(prefix="labrecorder_", suffix=".cfg")

        with os.fdopen(fd, "w", encoding="utf-8") as config_file:
            config_file.write("RCSEnabled=1\n")
            config_file.write(f"RCSPort={LABRECORDER_RCS_PORT}\n")

        return path

    def _wait_for_rcs_socket(self):
        deadline = time.time() + LABRECORDER_STARTUP_TIMEOUT
        last_error = None

        while time.time() < deadline:
            try:
                return socket.create_connection(
                    (LABRECORDER_RCS_HOST, LABRECORDER_RCS_PORT),
                    timeout=1,
                )
            except OSError as error:
                last_error = error
                time.sleep(0.5)

        raise RuntimeError(
            "LabRecorder no expuso el puerto de control remoto a tiempo."
        ) from last_error

    def _send_command(self, command):
        self._rcs_socket.sendall(f"{command}\n".encode("utf-8"))


def create_recording_backend(session_config):
    return XDFRecordingBackend(session_config)


def _build_output_path(session_config, extension):
    folder = _build_session_folder(session_config)
    os.makedirs(folder, exist_ok=True)

    filename = f"{session_config.build_basename()}.{extension}"

    return os.path.abspath(os.path.join(folder, filename))


def _build_session_folder(session_config):
    return os.path.join(
        DATA_DIR,
        session_config.target_slug,
        session_config.protocol_slug,
        session_config.stimulus_gender,
        str(session_config.subject_number),
    )
