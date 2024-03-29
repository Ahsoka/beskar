import logging, logging.handlers
import datetime
import pathlib

# NOTE: Adapted from: https://github.com/Ahsoka/bdaybot/blob/master/bdaybot/logs.py


class PrettyFormatter(logging.Formatter):
    def __init__(self, *args, style='%', **kwargs):
        if style != '%':
            raise ValueError(f"__init__() does not currently accept {style} as valid style, please use %")
        super().__init__(*args, style=style, **kwargs)

    def levelname_in_front(self):
        loc = self._fmt.find('%(levelname)s')
        if loc == -1:
            return False
        return ')s' not in self._fmt[:loc]

    def format(self, record):
        unparsed = super().format(record)
        if not self.levelname_in_front():
            return unparsed
        levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        max_length = max(map(len, levels))
        for index, level in enumerate(levels):
            if level in unparsed:
                break
        end_loc = unparsed.find(level) + len(level)
        end = unparsed[end_loc]
        while end != ' ':
            end_loc += 1
            end = unparsed[end_loc]
        spaces = max_length - len(level)
        returning = (" " * spaces) +  unparsed[:end_loc] + unparsed[end_loc:]
        # print(f"returning == unparsed = {unparsed == returning}")
        return returning


def file_renamer(filename: str):
    split = filename.split('.')
    return ".".join(split[:-3] + [split[-1], split[-2]])

def setUpLogger(
    name,
    logs_dir: pathlib.Path,
    fmt='%(levelname)s | %(name)s: [%(funcName)s()] %(message)s',
    file_name: str = None
):
    # Init the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Init the PrettyFormatter
    pretty = PrettyFormatter(fmt=fmt)

    # Create a handler that records all activity
    if isinstance(file_name, str):
        everything = logging.FileHandler(logs_dir / file_name, encoding='UTF-8')
    elif file_name is None:
        everything = logging.handlers.TimedRotatingFileHandler(
            logs_dir / f'{format(datetime.datetime.today(), "%Y-%m-%d")}.log',
            when='midnight',
            encoding='UTF-8'
        )
    else:
        raise TypeError(f"{file_name} must be str type, not '{type(file_name)}'.")
    # Do not use loggging.NOTSET, does not work for some reason
    # use logging.DEBUG if you want the lowest level
    everything.setLevel(logging.DEBUG)
    everything.setFormatter(pretty)

    # Rename files so .log is the file extension
    everything.namer = file_renamer

    # Add handlers to the logger
    logger.addHandler(everything)

    # Create a handler so we can see the output on the console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(pretty)

    # Add handler to the logger
    logger.addHandler(console)

    return logger
