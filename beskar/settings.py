from contextlib import contextmanager
from typing import Literal, Union

import logging
import pathlib
import json
import os

sentinel = object()

logger = logging.getLogger(__name__)

if os.name == 'nt':
    location = os.environ.get('APPDATA')
    if location:
        app_data = pathlib.Path(location)
    else:
        app_data = pathlib.Path.home() / 'AppData' / 'Roaming'
    logging_dir = app_data / 'Beskar' / 'logs'
    if not logging_dir.parent.exists():
        logging_dir.parent.mkdir()
    if not logging_dir.exists():
        logging_dir.mkdir()
else:
    logging_dir = pathlib.Path('logs')
    if not logging_dir.exists():
        logging_dir.mkdir()

logger.info(f'Logging directory set to {logging_dir}.')


class Settings:
    def __init__(self, location: Union[str, Literal[r'C:\Program Data']] = None):
        if os.name == 'nt':
            if location is None:
                try:
                    location = os.environ['PROGRAMDATA']
                except KeyError:
                    location = None
                if not location:
                    location = r'C:\ProgramData'
            self.settings_path = pathlib.Path(location) / 'Beskar' / 'settings.json'
        else:
            self.settings_path = pathlib.Path('settings.json')
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

        logger.info(f'Settings file path set to {self.settings_path}.')

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
        logger.info(f'Settings {key!r} has been set to {value}.')

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
