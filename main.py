import os
from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parent
    psychopy_appdata = project_root / ".psychopy-appdata"
    psychopy_appdata.mkdir(exist_ok=True)
    os.environ["APPDATA"] = str(psychopy_appdata)

    from core.app_controller import AppController

    controller = AppController()
    controller.run()


if __name__ == "__main__":
    main()
