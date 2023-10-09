import logging
import os
import shutil
import subprocess

from .build import extract_tgz_file
from .github import download_release
from threading import Thread, Lock
from typing import Any, Dict


class Installer(Thread):
    def __init__(self, package_info: Dict[str, Any], logger: logging.Logger, cleanup: bool = True) -> None:
        super().__init__()
        self.package_info = package_info
        self.is_installing = False
        self.status = ''
        self.msg = ''
        self.lock = Lock()
        self.logger = logger
        self.cleanup = cleanup
        self.extracted_to = ''
        self.logger.info('created installer')

    def run(self) -> None:
        self.logger.info('attempting to start installer thread')
        self.run_build()

    def set_status(self, status, msg):
        self.logger.info(f'setting status: {status}, {msg}')
        with self.lock:
            self.status = status
            self.msg = msg
        self.logger.info('setting status done')

    def run_build(self):
        """
        run a build:
        - fetch gitHub files
        - extract
        - install
        - cleanup
        """
        self.logger.info(f'run_build starting')
        self.set_status(
            'FETCH',
            f'attempting to get ' +
            f'{self.package_info["org"]}-{self.package_info["repo"]}-{self.package_info["release"]} from github'
        )
        try:
            tar_gz_fn = download_release(
                self.package_info['org'],
                self.package_info['repo'],
                self.package_info['release']
            )
            self.set_status('EXTRACT', f'attempting to extract f{tar_gz_fn} file')

            self.extracted_to = extract_tgz_file(tar_gz_fn)
            self.set_status('BUILD', f'attempting to run make for {self.extracted_to}/Makefile')
            # execute build steps
            make_opts = self.package_info['make_opts']
            make_cmd_list = ['make', '-C', self.extracted_to]
            target = ''
            for opt in make_opts.keys():
                if opt == 'TARGET':
                    target = make_opts['TARGET']
                else:
                    make_cmd_list.append(f'{opt}={make_opts[opt]}')
            if target == '':
                self.set_status('BUILD_FAILURE', f'cannot execute make as TARGET was not defined')
                return
            make_cmd_list.append(target)
            make_return = subprocess.run(make_cmd_list, capture_output=True)
            if make_return.returncode != 0:
                self.set_status(
                    'BUILD_FAILURE',
                    f'rc:{make_return.returncode}, stdout={make_return.stdout}. stderr={make_return.stderr}'
                )
                return

            self.set_status('BUILD_SUCCESS', 'successfully built application')

            # remove extracted dir
            if self.cleanup:
                if os.path.exists(self.extracted_to):
                    shutil.rmtree(self.extracted_to)
                self.set_status('CLEANUP_SUCCESS', f'successfully removed {self.extracted_to}')
        except Exception as e:
            self.logger.error(f'failed to run build: {e}')
            self.set_status('BUILD_FAILURE', f'failed to execute build: {e}')
