import argparse
import os
from pathlib import Path


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="NeuroEsfera BCI")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Muestra los trials sin casco, sin LabRecorder y sin guardar XDF.",
    )
    parser.add_argument(
        "--preview-trials-per-class",
        type=int,
        default=None,
        help="Solo en preview: cambia temporalmente los trials por clase.",
    )
    return parser.parse_args(args)


def main():
    args = parse_args()
    project_root = Path(__file__).resolve().parent
    psychopy_appdata = project_root / ".psychopy-appdata"
    psychopy_appdata.mkdir(exist_ok=True)
    os.environ["APPDATA"] = str(psychopy_appdata)

    from core.app_controller import AppController

    controller = AppController(
        preview_mode=args.preview,
        preview_trials_per_class=args.preview_trials_per_class,
    )
    controller.run()


if __name__ == "__main__":
    main()
