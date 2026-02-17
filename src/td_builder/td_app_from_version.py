import winreg
from dataclasses import dataclass
from pathlib import Path


@dataclass
class tdVersion:
    name: str
    version: str
    path: str

    def __repr__(self) -> str:
        return f"{self.name} | {self.version} | {self.path}"


def windows_get_installed_versions(app_name="TouchDesigner") -> dict[str, tdVersion]:
    exclude_apps: list[str] = ["TouchDesigner Dependency Manager"]

    # The registry paths where Windows stores "Uninstall" info
    paths = [
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        ),
    ]

    results: dict[str, tdVersion] = {}

    for hive, path in paths:
        try:
            # Access the registry key
            with winreg.OpenKey(hive, path) as key:
                # Iterate through every subkey (individual software entry)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            # Pull the Name and Version
                            # Not every key has these, so we use a try/except
                            name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                            install_path = Path(
                                winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            )
                            exe_path = install_path / "bin/TouchDesigner"

                            if name in exclude_apps:
                                pass
                            else:
                                if app_name.lower() in name.lower():
                                    new_td_version: tdVersion = tdVersion(
                                        name=name,
                                        version=version,
                                        path=exe_path.as_posix(),
                                    )
                                    results[version] = new_td_version
                    except (OSError, FileNotFoundError):
                        continue
        except FileNotFoundError:
            continue

    return results
