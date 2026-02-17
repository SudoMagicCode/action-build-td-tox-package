import os
import shutil
import subprocess
import sys

import td_builder

artifact_dir_name = "artifacts"
targets_dir_name = "targets"

dist_info: dict = {}


def verify_output_dirs(targetDir: str) -> None:
    # Verify dist directory exists
    td_builder.log_event("verifying output directories are created...")
    if not os.path.isdir(targetDir):
        td_builder.log_event("creating directories...", indent=1)
        os.makedirs(targetDir, exist_ok=True)


def start_td_project(build_settings: td_builder.build_settings.settings) -> None:
    # find all TouchDesigner versions on this machine
    system_td_versions: dict[str, td_builder.tdVersion] = (
        td_builder.windows_get_installed_versions()
    )

    td_builder.log_event("TD Versions on Local System", indent=1)
    for each in system_td_versions.values():
        td_builder.log_event(f"{each.name}", indent=2)

    version_dict = {each.version: each for each in system_td_versions.values()}
    if build_settings.td_version not in version_dict.keys():
        td_builder.log_event(
            f"Unable to locate TouchDesigner {build_settings.td_version} on this machine, exiting",
            indent=2,
        )
        exit()

    else:
        # run td project
        td_builder.log_event("Starting TouchDesigner", indent=2)
        td_version = version_dict.get(build_settings.td_version)
        subprocess.call([td_version.path, build_settings.project_file])


def build_tox_package(build_settings: td_builder.build_settings.settings):
    """ """

    td_builder.log_event("building tox package...")

    # Verify dist directory exists
    dist_dir = f"{build_settings.dest_dir}/"
    verify_output_dirs(dist_dir)

    td_builder.log_event("Starting deploy process...")

    td_builder.log_event("Finding Version Info...", indent=1)
    dist_info = td_builder.distInfo.distInfo()

    td_builder.log_event(
        f"Creating build {dist_info.major}.{dist_info.minor}.{dist_info.patch}",
        indent=2,
    )

    # set up env vars
    td_builder.env_var_utils.set_env_vars(
        build_settings=build_settings.env_vars, dist_info=dist_info
    )

    # fetch TDM dependencies
    if build_settings.use_tdm:
        td_builder.log_event("Fetch TDM elements", indent=2)
        subprocess.call(["tdm", "install"], cwd="./TouchDesigner/")

    # start TD Project
    start_td_project(build_settings)

    # check TD log files
    td_builder.read_td_log.write_log_to_cloud(build_settings.log_file)

    # zip release
    td_builder.log_event("Zipping package", indent=2)
    shutil.make_archive(
        build_settings.package_dir, "zip", root_dir=build_settings.package_dir
    )

    # cleanup environment variable keys
    td_builder.env_var_utils.clear_env_vars(build_settings=build_settings.env_vars)


def build_inventory(build_settings: td_builder.build_settings.settings):
    """ """

    td_builder.log_event("building tox inventory...")

    # Verify dist directory exists
    dist_dir = f"{build_settings.dest_dir}/"
    verify_output_dirs(dist_dir)

    td_builder.log_event("Starting deploy process...")
    td_builder.log_event("Finding Version Info...", indent=1)

    dist_info = td_builder.distInfo.distInfo()

    print(f"--> Creating build {dist_info.major}.{dist_info.minor}.{dist_info.patch}")
    td_builder.log_event(
        f"Creating build {dist_info.major}.{dist_info.minor}.{dist_info.patch}",
        indent=2,
    )

    # set up env vars
    td_builder.env_var_utils.set_env_vars(
        build_settings=build_settings.env_vars, dist_info=dist_info
    )

    # fetch TDM dependencies
    if build_settings.use_tdm:
        td_builder.log_event("Fetch TDM elements", indent=2)
        subprocess.call(["tdm", "install"], cwd="./TouchDesigner/")

    # start TD Project
    start_td_project(build_settings)

    # check TD log files
    td_builder.read_td_log.write_log_to_cloud(build_settings.log_file)

    # cleanup environment variable keys
    td_builder.env_var_utils.clear_env_vars(build_settings=build_settings.env_vars)


def main():
    print("> creating release...")
    print("> checking buildSettings.json ...")
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
