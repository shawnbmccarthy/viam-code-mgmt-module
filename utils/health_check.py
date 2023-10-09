import requests

from typing import Any, Dict


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

    return results
