import asyncio
import sys

from components import CodeMgmtSensor
from viam.components.sensor import Sensor
from viam.module.module import Module


async def main(addr: str) -> None:
    """
    Main entry into module, we will add our simple web_sensor for the web application
    deployed in the demo

    :param addr:
    :return:
    """
    m = Module(addr)
    m.add_model_from_registry(Sensor.SUBTYPE, CodeMgmtSensor.MODEL)
    await m.start()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('need socket path as command line arg')
    asyncio.run(main(sys.argv[1]))
