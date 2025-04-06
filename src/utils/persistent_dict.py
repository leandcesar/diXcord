from __future__ import annotations

import json
import os
import typing as t


class PersistentDict(dict):  # noqa: N801
    def __init__(self, file_path: str, *args, **kwargs) -> None:
        self.file_path = file_path
        super().__init__(*args, **kwargs)
        self._save()

    @classmethod
    def from_file(cls, file_path: str, /) -> PersistentDict:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if os.path.exists(file_path):
            with open(file_path) as f:
                data = json.load(f)
        else:
            data = {}
        return cls(file_path, data)

    def _save(self) -> None:
        with open(self.file_path, "w") as file:
            json.dump(self, file, indent=4)

    def __contains__(self, key: object) -> bool:
        try:
            self.__getitem__(key)
        except KeyError:
            return False
        else:
            return True

    def __setitem__(self, key: object, value: t.Any) -> None:
        if isinstance(key, int):
            key = str(key)
        super().__setitem__(key, value)
        self._save()

    def __getitem__(self, key: object) -> t.Any:
        if super().__contains__(key):
            return super().__getitem__(key)
        if isinstance(key, int) and super().__contains__(str(key)):
            return super().__getitem__(str(key))
        if isinstance(key, str) and key.isdigit() and super().__contains__(int(key)):
            return super().__getitem__(int(key))
        raise KeyError(f"Key {key} not found")

    def __delitem__(self, key: object) -> None:
        if super().__contains__(key):
            super().__delitem__(key)
        elif isinstance(key, int) and super().__contains__(str(key)):
            super().__delitem__(str(key))
        elif isinstance(key, str) and key.isdigit() and super().__contains__(int(key)):
            super().__delitem__(int(key))
        else:
            raise KeyError(f"Key {key} not found")
        self._save()

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        self._save()

    def pop(self, key: object, default: t.Any = None) -> t.Any:
        if key in self:
            value = self[key]
            del self[key]
            self._save()
            return value
        if default is not None:
            return default
        raise KeyError(f"Key {key} not found")

    def clear(self) -> None:
        super().clear()
        self._save()
