from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re

from core.config import DATA_DIR

from core.protocol_catalog import (
    get_protocol_config,
    get_stimulus_gender_config,
    get_target_config,
)


@dataclass
class SessionConfig:
    protocol_code: str
    protocol_slug: str
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

    @classmethod
    def for_protocol(
        cls,
        protocol_key,
        target_key,
        stimulus_gender,
        subject_number,
        trials_per_class,
        session_number=None,
    ):
        protocol = get_protocol_config(protocol_key)
        target = get_target_config(target_key)
        gender = get_stimulus_gender_config(stimulus_gender)
        resolved_session_number = session_number or _next_session_number(
            protocol,
            target,
            gender,
            stimulus_gender,
            subject_number,
        )

        return cls(
            protocol_code=protocol["code"],
            protocol_slug=protocol["slug"],
            protocol_name=protocol["label"],
            target_code=target["code"],
            target_slug=target["slug"],
            target_name=target["label"],
            stimulus_gender=stimulus_gender,
            stimulus_gender_code=gender["code"],
            subject_number=subject_number,
            session_number=resolved_session_number,
            total_trials=trials_per_class * protocol["total_trials_multiplier"],
            session_date=datetime.now().strftime("%d%m%y"),
        )

    @classmethod
    def for_motor_imagery(cls, subject_number, trials_per_class):
        return cls.for_protocol(
            "motor_imagery",
            "left_vs_right",
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
            f"{self.total_trials:02d}-"
            f"{self.session_date}"
        )


def _next_session_number(protocol, target, gender, stimulus_gender, subject_number):
    folder = _session_folder(target["slug"], protocol["slug"], stimulus_gender, subject_number)

    if not folder.exists():
        return 1

    xdf_files = list(folder.glob("*.xdf"))
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


def _session_folder(target_slug, protocol_slug, stimulus_gender, subject_number):
    return (
        Path(DATA_DIR)
        / target_slug
        / protocol_slug
        / stimulus_gender
        / str(subject_number)
    )
