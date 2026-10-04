from typing import Mapping


def inject_credentials(credentials, **kwarks):
    def join(first: dict, second: dict):
        for key, value in second.items():
            if key not in first:
                first[key] = value
            elif isinstance(value, Mapping):
                first[key] = join(first[key], value)

        return first

    return join(kwarks, credentials)
