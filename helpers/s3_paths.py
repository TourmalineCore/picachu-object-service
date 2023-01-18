from pathlib import PurePosixPath


def append_prefix(path: str, prefix: str = None) -> str:
    active_path = PurePosixPath(path)

    if active_path.is_absolute():
        active_path = PurePosixPath(*active_path.parts[1:])

    result_path: PurePosixPath = PurePosixPath(prefix, active_path) if prefix else active_path
    return str(result_path)
