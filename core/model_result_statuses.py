from enum import Enum


class ModelResultStatuses(str, Enum):
    FAILED = 'FAILED'
    SUCCESSFUL = 'SUCCESSFUL'
