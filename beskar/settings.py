from contextlib import contextmanager
from typing import Literal, Union

import pathlib
import json
import os

location = None
try:
    location = os.environ['PROGRAMDATA']
except KeyError:
    location = None
if not location:
    location = r'C:\ProgramData'

sentinel = object()

class Settings:
    def __init__(self, location: Union[str, Literal[r'C:\Program Data']] = location):
        self.settings_path = pathlib.Path(location) / 'Beskar' / 'settings.json'
        if self.settings_path.exists():
            file_healthy = True
            with self.settings_path.open() as file:
                try:
                    json.load(file)
                except json.JSONDecodeError:
                    file_healthy = False
            if not file_healthy:
                with self.settings_path.open(mode='w') as file:
                    json.dump({}, file)
        else:
            self.create()

    def __getitem__(self, key):
        with self.check_or_create() as exists:
            if exists:
                with self.settings_path.open() as file:
                    return json.load(file)[key]
            else:
                raise KeyError(key)

    def __setitem__(self, key, value):
        try:
            with self.settings_path.open(mode='r') as file:
                settings = json.load(file)
        except FileNotFoundError:
            settings = {}

        settings[key] = value
        self.create(settings, indent=4)

    def get(self, key, default=sentinel):
        try:
            return self[key]
        except KeyError:
            if default is not sentinel:
                return default
            else:
                raise

    def create(self, dumping=None, indent=None):
        if dumping is None:
            dumping = {}
        if not self.settings_path.parent.exists():
            self.settings_path.parent.mkdir()
        with self.settings_path.open(mode='w') as file:
            json.dump(dumping, file, indent=indent)

    @contextmanager
    def check_or_create(self):
        try:
            yield self.settings_path.exists()
        finally:
            if not self.settings_path.exists():
                self.create()
