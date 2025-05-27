from enum import Enum


class tox_build_contents(Enum):
    toxFiles = 'toxFiles'
    packageZip = 'packageZip'
    undefined = 'undefined'
