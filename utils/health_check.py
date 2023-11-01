import requests
import os
import logging

from typing import Any, Dict
from viam.logging import getLogger

logger: logging.Logger = getLogger(__name__)

def run_health_check(properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    run a simple health check
    """
    results = {}
    if properties['type'] == 'web':
        for i in properties['web_urls']:
            try:
                response = requests.get(i)
                results[i] = {
                    'status_code': response.status_code,
                }
                if response.status_code == 200:
                    results[i]['content'] = response.json()
                else:
                    results[i]['content'] = 'none'
            except Exception as e:
                results[i] = {'status': f'failed to connect: {e}'}
    elif properties['type'] == 'ros2_ws':
        try:
            if os.path.exists(properties['install_dir']):
                results['status'] = 'Installed'
                dirs= os.listdir(properties['install_dir'] + '/src')         
                results['nodes'] = dirs 
            else:
                results['status'] = 'Not installed'
        except KeyError as e:
            logger.error("Error: no install_dir")
            results['status'] = 'N/A'
    return results
