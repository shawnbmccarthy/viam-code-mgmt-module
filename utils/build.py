"""
some utility functions
"""
import os
import tarfile

from typing import Any, Dict


def extract_tgz_file(tar_gz_fn: str) -> str:
    """
    extract the file and return the prefix of the directory it was
    extracted to
    """
    tf = tarfile.open(tar_gz_fn, 'r:gz')
    tf.extractall()
    return os.path.commonpath(tf.getnames())


def should_install(
        previous_package: Dict[str, Any] | None,
        current_package: Dict[str, Any]
) -> bool:
    """
    based on previous state & current state of package info
    should we do an install
    """
    if previous_package is None:
        filename = f'{current_package["org"]}-{current_package["repo"]}-{current_package["release"]}.tar.gz'
        if not os.path.isfile(filename):
            return True
    else:
        # Finally, reconfigure executed, was it this component?
        previous_r = f'{previous_package["org"]}-{previous_package["repo"]}-{previous_package["release"]}'
        current_r = f'{current_package["org"]}-{current_package["repo"]}-{current_package["release"]}'
        if previous_r != current_r:
            return True
    return False
