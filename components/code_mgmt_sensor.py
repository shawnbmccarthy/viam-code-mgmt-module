"""
This example will show how we manage the latest gitHub release
"""
import logging

from datetime import datetime as dt
from utils import build, installer, health_check
from typing import Any, ClassVar, Dict, List, Mapping, Optional, Sequence
from typing_extensions import Self

from google.protobuf.json_format import MessageToDict
from viam.components.component_base import ValueTypes
from viam.components.sensor import Sensor
from viam.logging import getLogger
from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily

logger: logging.Logger = getLogger(__name__)


class CodeMgmtSensor(Sensor, Reconfigurable):
    """
    Simple sensor which will deploy and manage applications based on attributes
    found in the configuration.
    """
    MODEL: ClassVar[Model] = Model(ModelFamily('shawns-modules', 'code-mgmt'), 'sensor')
    HEALTH_CHECK_KEYS: List[str] = ['type']
    PACKAGE_INFO_KEYS: List[str] = ['org', 'repo', 'release', 'make_opts']

    health_check: Dict[str, Any] | None
    package_info: Dict[str, Any] | None
    install_thread: installer.Installer | None

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        """
        create new instance of web sensor

        :param config:
        :param dependencies:
        :return:
        """
        sensor = cls(config.name)

        sensor.health_check = None
        sensor.package_info = None
        sensor.install_thread = None
        sensor.reconfigure(config, dependencies)
        return sensor

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """
        validate configuration

        :param config:
        :return:
        """
        health_check = MessageToDict(config.attributes.fields['health_check'])
        if health_check is None or len(health_check.keys()) == 0:
            raise Exception('health_check dictionary required, please see README.md')

        hc_k = health_check.keys()
        for k in cls.HEALTH_CHECK_KEYS:
            if k not in hc_k:
                raise Exception(f'health_check requires {k}, please see README.md')

        package_info = MessageToDict(config.attributes.fields['package_info'])
        if package_info is None or len(health_check.keys()) == 0:
            raise Exception('package_info dictionary required, please see README.md')

        pi_k = package_info.keys()
        for k in cls.PACKAGE_INFO_KEYS:
            if k not in pi_k:
                raise Exception(f'package_info requires {k}, please see README.md')

        return []

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> None:
        """
        reconfigure component

        :param config:
        :param dependencies:
        :return:
        """

        # is an install running (edge case, wait for it to complete - could cause a timeout)
        if self.install_thread is not None:
            self.install_thread.join()

        self.health_check = MessageToDict(config.attributes.fields['health_check'])
        package_info = MessageToDict(config.attributes.fields['package_info'])

        if build.should_install(self.package_info, package_info):
            logger.info('attempting to start install')
            self.install_thread = installer.Installer(package_info, logger)
            self.install_thread.start()
        else:
            logger.info('no install needed')

        self.package_info = package_info

    async def get_readings(
            self,
            *,
            extra: Optional[Mapping[str, Any]] = None,
            timeout: Optional[float] = None, **kwargs
    ) -> Mapping[str, Any]:
        """
        :param extra:
        :param timeout:
        :param kwargs:
        :return:
        """
        if self.install_thread is not None:
            while self.install_thread.is_alive():
                return {
                    'install_status': self.install_thread.status,
                    'install_msg': self.install_thread.msg,
                    'install_at': str(dt.now())
                }

            # thread is finished
            self.install_thread.join()
            logger.info(f'get_readings: {self.install_thread.status}, {self.install_thread.msg}')
            if self.install_thread.status == 'BUILD_FAILURE':
                return {
                    'install_status': self.install_thread.status,
                    'install_msg': self.install_thread.msg,
                    'install_at': str(dt.now())
                }
            else:
                self.install_thread = None

        return health_check.run_health_check(self.health_check)

    async def do_command(
            self,
            command: Mapping[str, ValueTypes],
            *,
            timeout: Optional[float] = None,
            **kwargs
    ) -> Mapping[str, ValueTypes]:
        """
        not implemented right now

        :param command:
        :param timeout:
        :param kwargs:
        :return:
        """
        pass


"""
Register the new MODEL as well as define how the object is validated 
and created
"""
Registry.register_resource_creator(
    Sensor.SUBTYPE,
    CodeMgmtSensor.MODEL,
    ResourceCreatorRegistration(CodeMgmtSensor.new, CodeMgmtSensor.validate_config)
)
