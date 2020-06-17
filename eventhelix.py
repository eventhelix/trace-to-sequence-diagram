import os
import sys

import config
from funutils import just, Maybe, first


def generate_output_with_eventstudio():
    """
    Run EventStudio to automatically generate the sequence diagram.
    """
    if sys.platform == 'win32':
        eventstudio_directory = just(config.eventstudio_path) if config.eventstudio_path else find_eventstudio_vscode_path(
            os.path.expandvars(config.vscode_extensions))
        eventstudio = eventstudio_directory.map(lambda p: os.path.join(p, 'evstudio.exe'))
    elif sys.platform == 'darwin':
        eventstudio_directory = just(config.eventstudio_path) if config.eventstudio_path else find_eventstudio_vscode_path(
            os.path.expanduser(config.vscode_extensions))
        eventstudio = eventstudio_directory.map(lambda p: os.path.join(p, 'evstudio'))
    else:
        print('Unsupported platform')
        exit()

    command_line = eventstudio.map(lambda p: str.format(config.eventstudio_command_line, eventStudio=f'"{p}"'))
    if command_line.hasValue:
        os.system(command_line.value)
    else:
        print('Could not find EventStudio')
        exit()


def find_eventstudio_vscode_path(extensions_path) -> Maybe[str]:
    return first(os.listdir(extensions_path),
                 lambda x: os.path.basename(x).lower().startswith('eventhelix.eventstudio-')).map(
        lambda p: os.path.join(extensions_path, p))
