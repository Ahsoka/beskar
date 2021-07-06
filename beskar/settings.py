from typing import Literal, Union
from contextlib import contextmanager

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

class Settings:
    def __init__(self, location: Union[str, Literal[r'C:\Program Data']] = location):
        self.settings_path = pathlib.Path(location) / 'Beskar' / 'settings.json'
        if not self.settings_path.exists():
            self.create()

    def __getitem__(self, key):
        with self.check_or_create() as exists:
            if exists:
                with self.settings_path.open() as file:
                    return json.load(file)[key]
            else:
                raise KeyError(key)

    def __setitem__(self, key, value):
        with self.settings_path.open(mode='r+') as file:
            try:
                settings = json.load(file)
            except FileNotFoundError:
                settings = {}
            settings[key] = value
            json.dump(settings, file, indent=4)

    def create(self):
        if not self.settings_path.parent.exists():
            self.settings_path.parent.mkdir()
        with self.settings_path.open(mode='w') as file:
            json.dump({}, file)

    @contextmanager
    def check_or_create(self):
        try:
            yield self.settings_path.exists()
        finally:
            if not self.settings_path.exists():
                self.create()
