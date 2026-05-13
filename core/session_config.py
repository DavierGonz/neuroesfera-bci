from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re

from core.config import DATA_DIR

from core.protocol_catalog import (
    get_block_config,
    get_protocol_config,
    get_stimulus_gender_config,
    get_target_config,
)


@dataclass
class SessionConfig:
    protocol_code: str
    protocol_slug: str
    dataset_slug: str
    protocol_name: str
    target_code: str
    target_slug: str
    target_name: str
    stimulus_gender: str
    stimulus_gender_code: str
    subject_number: int
    session_number: int
    total_trials: int
    session_date: str
    block_key: str | None = None
    block_label: str | None = None
    block_folder: str | None = None

    @classmethod
    def for_protocol(
        cls,
        protocol_key,
        stimulus_gender,
        subject_number,
        trials_per_class,
        block_key=None,
        session_number=None,
    ):
        protocol = get_protocol_config(protocol_key)
        target = get_target_config(protocol["target_key"])
        gender = get_stimulus_gender_config(stimulus_gender)
        block = _resolve_block(protocol, block_key)
        resolved_session_number = session_number or _next_session_number(
            protocol,
            target,
            gender,
            stimulus_gender,
            subject_number,
            block,
        )

        return cls(
            protocol_code=protocol["code"],
            protocol_slug=protocol["slug"],
            dataset_slug=protocol.get("dataset_slug", protocol["slug"]),
            protocol_name=protocol["label"],
            target_code=target["code"],
            target_slug=target["slug"],
            target_name=target["label"],
            stimulus_gender=stimulus_gender,
            stimulus_gender_code=gender["code"],
            subject_number=subject_number,
            session_number=resolved_session_number,
            total_trials=protocol.get(
                "total_trials",
                trials_per_class * protocol.get("total_trials_multiplier", 0),
            ),
            session_date=datetime.now().strftime("%d%m%y"),
            block_key=block["key"] if block else None,
            block_label=block["label"] if block else None,
            block_folder=block["folder"] if block else None,
        )

    @classmethod
    def for_motor_imagery(cls, subject_number, trials_per_class):
        return cls.for_protocol(
            "experiment_1",
            "hombre",
            subject_number,
            trials_per_class,
        )

    def build_basename(self):
        return (
            f"{self.protocol_code}-"
            f"{self.target_code}-"
            f"{self.stimulus_gender_code}-"
            f"SUJETO{self.subject_number:02d}-"
            f"SESION{self.session_number:02d}-"
            f"T{self.total_trials:02d}-"
            f"{self.session_date}"
        ).upper()


def _resolve_block(protocol, block_key):
    if not protocol.get("requires_block"):
        return None

    resolved_key = block_key or protocol["block_keys"][0]
    block = dict(get_block_config(resolved_key))
    block["key"] = resolved_key
    return block


def _next_session_number(protocol, target, gender, stimulus_gender, subject_number, block):
    folder = _subject_folder(protocol, stimulus_gender, subject_number)
    if block:
        xdf_files = [xdf_file for xdf_file in folder.rglob("*.xdf") if xdf_file.is_file()]
    else:
        xdf_files = [xdf_file for xdf_file in folder.glob("*.xdf") if xdf_file.is_file()]

    if not xdf_files:
        return 1

    prefix = (
        f"{protocol['code']}-{target['code']}-{gender['code']}-"
        f"SUJETO{subject_number:02d}-SESION"
    )
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)-.*\.xdf$", re.IGNORECASE)
    detected_sessions = []

    for xdf_file in xdf_files:
        match = pattern.match(xdf_file.name)
        if match:
            detected_sessions.append(int(match.group(1)))

    if detected_sessions:
        return max(detected_sessions) + 1

    return len(xdf_files) + 1


def build_session_folder(session_config):
    folder = (
        Path(DATA_DIR)
        / session_config.dataset_slug
        / session_config.stimulus_gender
        / str(session_config.subject_number)
    )

    if session_config.block_folder:
        folder = folder / session_config.block_folder

    return folder


def _subject_folder(protocol, stimulus_gender, subject_number):
    return (
        Path(DATA_DIR)
        / protocol.get("dataset_slug", protocol["slug"])
        / stimulus_gender
        / str(subject_number)
    )
