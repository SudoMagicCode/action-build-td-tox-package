import json
from pathlib import Path
from .tox_build_contents import tox_build_contents


class settings:
    REQUIRED_KEYS: list[str] = [
        "BUILD",
        "TD_VERSION",
        "PROJECT_FILE",
        "COMP_NAME",
        "BUILD_CONTENTS",
        "USE_TDM",
    ]

    def __init__(self):
        self.project_file: str
        self.td_version: str
        self.privacy: str
        self._build: str = "TRUE"
        self._project_name: str = "TBD"
        self.release_dir: Path = Path("artifacts")
        self.package_dir: Path = self.release_dir / "package"
        self.additional_keys: dict = {}
        self.use_tdm: bool = False
        self.build_contents: tox_build_contents = tox_build_contents.undefined

    def __repr__(self) -> str:
        return f'''----
        project_file {self.project_file}
        td_version {self.td_version}
        privacy {self.privacy}
        build {self._build}
        project_name {self._project_name}
        release_dir {self.release_dir}
        package_dir {self.package_dir}
        additional_keys {self.additional_keys}
        use_tdm {self.use_tdm}
        build_contents {self.build_contents}
        ---'''

    @property
    def log_file(self) -> Path:
        return self.release_dir / "log.txt"

    @property
    def dest_dir(self) -> Path:
        return self.package_dir / self.project_name

    @property
    def td_package_file(self) -> Path:
        return self.dest_dir / "tdmPackages.yml"

    @property
    def project_name(self) -> str:
        return self._project_name

    @property
    def build(self) -> str:
        return self._build

    @property
    def env_vars(self) -> dict:
        # build required keys
        env_vars = {
            "SM_BUILD": self.build,
            "SM_PRIVACY": "FALSE",
            "SM_SAVE_PATH": self.dest_dir.as_posix(),
            "SM_COMP_NAME": self.project_name,
            "SM_LOG_FILE": self.log_file.as_posix(),
            "SM_TD_PACKAGE_FILE": self.td_package_file.as_posix(),
            "SM_BUILD_CONTENTS": self.build_contents.value
        }

        # add additional keys
        if self.additional_keys != None:
            for key, value in self.additional_keys:
                env_vars[key] = value

        return env_vars

    def _tox_build_contents_from_name(self, name: str) -> tox_build_contents:
        """ """
        tox_content_map: dict = {
            tox_build_contents.packageZip.name: tox_build_contents.packageZip,
            tox_build_contents.toxFiles.name: tox_build_contents.toxFiles,
            tox_build_contents.undefined.name: tox_build_contents.undefined,
        }
        tox_content = tox_content_map.get(name, tox_build_contents.undefined)
        return tox_content

    def load_from_json(self, src_file: str) -> dict:
        print("-> loading build settings from file...")

        try:
            with open(src_file, "r") as file:
                data: dict = json.load(file)

                if set(settings.REQUIRED_KEYS) <= data.keys():
                    print("-> all required keys accounted for")
                    self._build = data.get("BUILD", "development")
                    self.td_version = data.get("TD_VERSION", "unknown")
                    self.project_file = data.get("PROJECT_FILE", "unknown")
                    self._project_name = data.get("COMP_NAME", "not-set")
                    self.use_tdm = data.get("USE_TDM", False)
                    self.build_contents = self._tox_build_contents_from_name(
                        data.get("BUILD_CONTENTS", "undefined")
                    )

                    for key, value in data.items():
                        if key in settings.REQUIRED_KEYS:
                            pass
                        else:
                            self.additional_keys[key] = str(value)

                    return data

                else:
                    print(
                        f"-> buildSettings missing required keys, {settings.REQUIRED_KEYS} must be present"
                    )
                    exit()

        except Exception as e:
            print(e)
            print(
                "-> unable to locate build settings, please ensure a 'buildSettings.json file is in the root of your project"
            )
            exit()

        return {}
