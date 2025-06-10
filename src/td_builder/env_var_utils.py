'''
A small library of utility functions for managing environment variables
'''

import os
from .distInfo import distInfo


def set_env_vars(build_settings: dict, dist_info: distInfo):
    '''A utility function to set environment variables'''

    print(f"-> Setting Environment Variables")
    for each_key, each_val in build_settings.items():
        _set_env_var(each_key, each_val)

    # set the sem-ver as a env var available to TouchDesigner
    semver = f"{dist_info.major}.{dist_info.minor}.{dist_info.patch}"
    _set_env_var("SM_TOXVERSION", semver)

    # set the repo url as a env var available to TouchDesigner
    repo_url = dist_info.remoteSource
    _set_env_var("SM_REPO", repo_url)


def _set_env_var(key: str, value: str) -> None:
    '''A utility function to set a single environment variable'''

    os.environ[key] = value
    print(f"--> setting var {key.upper()} = {value}")


def clear_env_vars(build_settings: dict):
    '''A utility function to remove a collection of environment variables'''

    print(f"-> Cleaning up Environment Variables")
    for each_key in build_settings.keys():
        _remove_env_var(each_key)
    _remove_env_var("SM_TOXVERSION")
    _remove_env_var("SM_REPO")


def _remove_env_var(key: str) -> None:
    '''A utility function to remove a single environment variable'''

    del os.environ[key]
    print(f"--> removing var {key.upper()}")
