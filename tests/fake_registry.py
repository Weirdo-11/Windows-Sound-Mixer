class FakeRegistryKey:
    def __init__(self, registry: "FakeRegistry", path: str) -> None:
        self._registry = registry
        self.path = path

    def __enter__(self) -> "FakeRegistryKey":
        return self

    def __exit__(self, *exc_info) -> None:
        return None


class FakeRegistry:
    HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
    KEY_READ = 1
    KEY_SET_VALUE = 2
    REG_SZ = 1

    def __init__(self) -> None:
        self._values: dict[str, dict[str, str]] = {}

    def OpenKey(self, root, path: str, reserved: int, access: int) -> FakeRegistryKey:
        return FakeRegistryKey(self, path)

    def SetValueEx(self, key: FakeRegistryKey, name: str, reserved: int, type_: int, value: str) -> None:
        self._values.setdefault(key.path, {})[name] = value

    def QueryValueEx(self, key: FakeRegistryKey, name: str) -> tuple[str, int]:
        values = self._values.get(key.path, {})
        if name not in values:
            raise FileNotFoundError(name)
        return values[name], self.REG_SZ

    def DeleteValue(self, key: FakeRegistryKey, name: str) -> None:
        values = self._values.get(key.path, {})
        if name not in values:
            raise FileNotFoundError(name)
        del values[name]
