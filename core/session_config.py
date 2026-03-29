from dataclasses import dataclass
from datetime import datetime


@dataclass
class SessionConfig:
    protocol_code: str
    protocol_slug: str
    subject_number: int
    experiment_number: int
    total_trials: int
    session_date: str

    @classmethod
    def for_motor_imagery(cls, subject_number, experiment_number, trials_per_class):
        return cls(
            protocol_code="MI",
            protocol_slug="motor_imagery",
            subject_number=subject_number,
            experiment_number=experiment_number,
            total_trials=trials_per_class * 2,
            session_date=datetime.now().strftime("%d%m%y"),
        )

    def build_basename(self):
        return (
            f"{self.protocol_code}-"
            f"{self.subject_number:02d}-"
            f"{self.experiment_number:02d}-"
            f"{self.total_trials:02d}-"
            f"{self.session_date}"
        )
