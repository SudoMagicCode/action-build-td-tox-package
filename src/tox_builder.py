import json
import subprocess
import os
import shutil
import sys

import td_builder

artifact_dir_name = "artifacts"
targets_dir_name = "targets"

dist_info: dict = {}


def build_tox_package(build_settings: td_builder.build_settings.settings):
    '''
    '''
    print('> building tox package...')

    # Verify dist directory exists
    dist_dir = f"{build_settings.dest_dir}/"
    print('> verifying output directories are created...')
    if not os.path.isdir(dist_dir):
        print('-> creating directories...')
        os.makedirs(dist_dir, exist_ok=True)

    print("> Starting deploy process...")

    print("-> Finding Version Info...")
    dist_info = td_builder.distInfo.distInfo()

    print(
        f"--> Creating build {dist_info.major}.{dist_info.minor}.{dist_info.patch}")

    # set up env vars
    td_builder.env_var_utils.set_env_vars(
        build_settings=build_settings.env_vars, dist_info=dist_info)

    # fetch TDM dependencies
    if build_settings.use_tdm:
        print("--> Fetch TDM elements")
        subprocess.call(['tdm', 'install'], cwd="./TouchDesigner/")

    # run td project
    print("--> Starting TouchDesigner")
    td_version = f"C:/Program Files/Derivative/TouchDesigner.{build_settings.td_version}/bin/TouchDesigner.exe"
    subprocess.call([td_version, build_settings.project_file])

    td_builder.read_td_log.write_log_to_cloud(
        build_settings.log_file)

    print("--> Zipping package")
    shutil.make_archive(
        build_settings.package_dir, 'zip', root_dir=build_settings.package_dir)

    # cleanup environment variable keys
    td_builder.env_var_utils.clear_env_vars(
        build_settings=build_settings.env_vars)


def build_inventory(build_settings: td_builder.build_settings.settings):
    '''
    '''
    print('> building tox inventory...')

    # Verify dist directory exists
    dist_dir = f"{build_settings.dest_dir}/"
    print('> verifying output directories are created...')
    if not os.path.isdir(dist_dir):
        print('-> creating directories...')
        os.makedirs(dist_dir, exist_ok=True)

    print("> Starting deploy process...")

    print("-> Finding Version Info...")
    dist_info = td_builder.distInfo.distInfo()

    print(
        f"--> Creating build {dist_info.major}.{dist_info.minor}.{dist_info.patch}")

    # set up env vars
    td_builder.env_var_utils.set_env_vars(
        build_settings=build_settings.env_vars, dist_info=dist_info)

    # fetch TDM dependencies
    if build_settings.use_tdm:
        print("--> Fetch TDM elements")
        subprocess.call(['tdm', 'install'], cwd="./TouchDesigner/")

    # run td project
    print("--> Starting TouchDesigner")
    td_version = f"C:/Program Files/Derivative/TouchDesigner.{build_settings.td_version}/bin/TouchDesigner.exe"
    subprocess.call([td_version, build_settings.project_file])

    td_builder.read_td_log.write_log_to_cloud(
        build_settings.log_file)

    # cleanup environment variable keys
    td_builder.env_var_utils.clear_env_vars(
        build_settings=build_settings.env_vars)


def main():
    print('> creating release...')
    print('> checking buildSettings.json ...')
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
