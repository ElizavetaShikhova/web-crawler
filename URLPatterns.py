import re
from dataclasses import dataclass

@dataclass
class URLPatterns:
    __URL_PATTERN: re.Pattern = re.compile(
        r'^(https?|ftp)://'  # Протокол
        r'([A-Za-z0-9.-]+)'  # Домен
        r'(:\d+)?'  # Порт (опционально)
        r'(/[^?#]*)?'  # Путь (опционально)
        r'(\?[^#]*)?$'  # Параметры (опционально)
    )
    __DOMAIN_PATTERN: re.Pattern = re.compile(
        r'^([A-Za-z0-9-]+\.)+[A-Za-z]{2,}$'
    )

    @property
    def URL_PATTERN(self):
        return self.__URL_PATTERN

    @property
    def DOMAIN_PATTERN(self):
        return self.__DOMAIN_PATTERN