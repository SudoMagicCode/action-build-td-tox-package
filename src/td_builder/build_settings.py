import json
from pathlib import Path
from .tox_build_contents import tox_build_contents
from .logging_utils import log_event


class settings:
    REQUIRED_KEYS: list[str] = [
        "BUILD",
        "TD_VERSION",
        "PROJECT_FILE",
        "COMP_NAME",
        "BUILD_CONTENTS",
        "USE_TDM",
    ]

    def __init__(
        self,
        projectFile: str,
        tdVersion: str,
        privacy: str,
        buildState: bool,
        projectName: str = 'TBD',
        releaseDir: str = 'artifacts',
        additionalKeys: dict = {},
        useTdm: bool = False,
        buildContents: tox_build_contents = tox_build_contents.undefined
    ):
        self.project_file = projectFile
        self.td_version = tdVersion
        self.privacy = privacy
        self.build = buildState
        self.project_name = projectName
        self.release_dir: Path = Path(releaseDir)
        self.package_dir: Path = self.release_dir / "package"
        self.additional_keys = additionalKeys
        self.use_tdm = useTdm
        self.build_contents = buildContents

    def __repr__(self) -> str:
        return f'''----
    project_file    {self.project_file}
    td_version      {self.td_version}
    privacy         {self.privacy}
    build           {self.build}
    project_name    {self.project_name}
    release_dir     {self.release_dir}
    package_dir     {self.package_dir}
    log_file        {self.log_file}
    additional_keys {self.additional_keys}
    use_tdm         {self.use_tdm}
    build_contents  {self.build_contents}
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
    def env_vars(self) -> dict:
        # build required keys
        env_vars = {
            "SM_BUILD": str(self.build).upper(),
            "SM_PRIVACY": str(self.privacy).upper(),
            "SM_SAVE_PATH": f"../{self.dest_dir.as_posix()}",
            "SM_COMP_NAME": self.project_name,
            "SM_LOG_FILE": f"../{self.log_file.as_posix()}",
            "SM_TD_PACKAGE_FILE": self.td_package_file.as_posix(),
            "SM_BUILD_CONTENTS": self.build_contents.value
        }

        # add additional keys
        if self.additional_keys != None:
            for key, value in self.additional_keys:
                env_vars[key] = value

        return env_vars

    @staticmethod
    def from_json(srcFile: str):
        log_event(msg="loading build settings from file...", indent=1)

        try:
            with open(srcFile, "r") as file:
                data: dict = json.load(file)
                additional_keys = {}

                if set(settings.REQUIRED_KEYS) <= data.keys():
                    log_event("all required keys accounted for", indent=1)

                    project_file_from_file = data.get(
                        "PROJECT_FILE", "unknown")
                    td_version_from_file = data.get("TD_VERSION", "unknown")
                    build_from_file = data.get("BUILD", False)
                    project_name_from_file = data.get("COMP_NAME", "not-set")
                    use_tdm_from_file = data.get("USE_TDM", False)
                    build_contents_from_file = tox_build_contents.from_str(
                        data.get("BUILD_CONTENTS", "undefined"))

                    for key, value in data.items():
                        if key in settings.REQUIRED_KEYS:
                            pass
                        else:
                            additional_keys[key] = str(value)

                    return settings(
                        projectFile=project_file_from_file,
                        tdVersion=td_version_from_file,
                        privacy=False,
                        buildState=build_from_file,
                        projectName=project_name_from_file,
                        useTdm=use_tdm_from_file,
                        buildContents=build_contents_from_file,
                        additionalKeys=additional_keys
                    )

                else:
                    log_event(
                        f"buildSettings missing required keys, {settings.REQUIRED_KEYS} must be present", indent=1, isError=True)
                    exit()

        except Exception as e:
            print(e)
            log_event(
                "unable to locate build settings, please ensure a 'buildSettings.json file is in the root of your project", indent=1, isError=True)
            exit()
