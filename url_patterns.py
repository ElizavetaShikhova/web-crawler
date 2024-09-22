import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Regex:
    protocol: str = r'^(https?|ftp)://'
    domain: str = r'([A-Za-z0-9.-]+)'
    port: str = r'(:\d+)?'
    path: str = r'(/[^?#]*)?'
    query: str = r'(\?[^#]*)?$'
    domain_only: str = r'^([A-Za-z0-9-]+\.)+[A-Za-z]{2,}$'

URL_PATTERN = re.compile(
    Regex.protocol +
    Regex.domain +
    Regex.port +
    Regex.path +
    Regex.query)

DOMAIN_PATTERN = re.compile(Regex.domain_only)