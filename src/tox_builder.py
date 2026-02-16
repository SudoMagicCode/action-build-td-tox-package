import os
import shutil
import subprocess
import sys
from pathlib import Path

import td_builder

artifact_dir_name = "artifacts"
targets_dir_name = "targets"

dist_info: dict = {}


def check_output_dir(outputDir) -> None:
    # Verify dist directory exists
    td_builder.output_utils.log_event("verifying output directories are created...")

    if not os.path.isdir(outputDir):
        td_builder.output_utils.log_event("creating directories...", indent=1)
        os.makedirs(outputDir, exist_ok=True)


def tdm_install() -> None:
    # fetch TDM dependencies
    td_builder.output_utils.log_event("Fetching all TDM elements")
    subprocess.call(["tdm", "install"], cwd="./TouchDesigner/")


def tdm_run() -> None:
    current_dir = Path.cwd()

    td_dir = current_dir / "TouchDesigner"
    td_builder.output_utils.log_event(f"moving to {td_dir}")
    os.chdir(td_dir)
    # start project with TDM
    td_builder.output_utils.log_event("starting project with tdm run")
    subprocess.call(["tdm", "run"])


def build_tox_package(build_settings: td_builder.build_settings.settings):
    """ """

    td_builder.output_utils.log_event("Building TOX package...")

    # verify output directory exists
    dist_dir = f"{build_settings.dest_dir}/"
    check_output_dir(dist_dir)

    td_builder.output_utils.log_event("Starting deploy process...")

    td_builder.output_utils.log_event("Finding Version Info...", indent=1)
    dist_info = td_builder.distInfo.distInfo()

    td_builder.output_utils.log_event(
        f"Creating build {dist_info.major}.{dist_info.minor}.{dist_info.patch}",
        indent=1,
    )

    # fetch TDM dependencies
    tdm_install()

    # run project with TDM
    tdm_run()

    td_builder.read_td_log.write_log_to_cloud(build_settings.log_file)

    td_builder.output_utils.log_event("Zipping package", indent=1)
    shutil.make_archive(
        build_settings.package_dir, "zip", root_dir=build_settings.package_dir
    )


def build_inventory(build_settings: td_builder.build_settings.settings):
    """ """
    td_builder.output_utils.log_event("building tox inventory...")

    # verify output directory exists
    dist_dir = f"{build_settings.dest_dir}/"
    check_output_dir(dist_dir)

    td_builder.output_utils.log_event("Starting deploy process...")
    td_builder.output_utils.log_event("Finding Version Info...", indent=1)

    dist_info = td_builder.distInfo.distInfo()

    td_builder.output_utils.log_event(
        f"Creating build {dist_info.major}.{dist_info.minor}.{dist_info.patch}",
        indent=1,
    )

    # fetch TDM dependencies
    tdm_install()

    # run project with TDM
    tdm_run()

    td_builder.read_td_log.write_log_to_cloud(build_settings.log_file)


def main():
    td_builder.output_utils.log_event("creating release...")
    td_builder.output_utils.log_event("checking buildSettings.json ...")

    settings_file_path: str = sys.argv[1]
    build_settings = td_builder.build_settings.settings()
    build_settings.load_from_json(settings_file_path)

    match build_settings.build_contents:
        case td_builder.tox_build_contents.packageZip:
            build_tox_package(build_settings=build_settings)

        case td_builder.tox_build_contents.toxFiles:
            build_inventory(build_settings=build_settings)
        case _:
            print("Missing build contents should be : packageZip or toxFiles")
            exit()


if __name__ == "__main__":
    main()
