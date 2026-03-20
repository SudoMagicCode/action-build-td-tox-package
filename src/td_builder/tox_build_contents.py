from enum import Enum


class tox_build_contents(Enum):
    toxFiles = 'toxFiles'
    packageZip = 'packageZip'
    undefined = 'undefined'

    @classmethod
    def from_str(cls, input_str: str):
        try:
            return cls[input_str]
        except KeyError:
            return cls.unknown
