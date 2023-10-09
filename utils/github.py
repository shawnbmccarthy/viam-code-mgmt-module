"""
TODO: Account for github tokens for API keys
"""
import requests

from typing import Dict

GITHUB_URL = 'https://api.github.com/repos'


def get_release_info(org: str, repo: str, release: str) -> Dict:
    """

    """
    url = ''
    if release != 'latest':
        url = f'{GITHUB_URL}/{org}/{repo}/releases/tags/{release}'
    else:
        url = f'{GITHUB_URL}/{org}/{repo}/releases/latest'

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'failed to retrieve release info for {url}')
    return response.json()


def download_release(org: str, repo: str, release: str = 'latest') -> str:
    """

    """
    filename = f'{org}-{repo}-{release}.tar.gz'

    data = get_release_info(org, repo, release)
    if data is None or 'tarball_url' not in data:
        raise Exception(f'failed to get valid release information: {data}')

    response = requests.get(data['tarball_url'])
    if response.status_code != 200:
        raise Exception(f'failed to get tarball: {data["tarball_url"]}')

    try:
        with open(filename, 'wb') as f:
            _ = f.write(response.content)
    except (ValueError | AttributeError) as e:
        # catch failure on binary write or content key not around
        raise Exception(e)

    return filename
