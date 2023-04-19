from enum import Enum, auto

class API_MODE(Enum):
    OPEN_AI = auto()
    AZURE = auto()
    AZURE_AD = auto()