import os
import sys

import config
from funutils import just, Maybe, first


def generateOutputWithEventStudio():
    """
    Run EventStudio to automatically generate the sequence diagram.
    """
    if sys.platform == 'win32':
        eventStudioDirectory = just(config.eventStudioPath) if config.eventStudioPath else findEventStudioVSCodePath(
            os.path.expandvars(config.vsCodeExtensions))
        eventStudio = eventStudioDirectory.map(lambda p: os.path.join(p, 'evstudio.exe'))
    elif sys.platform == 'darwin':
        eventStudioDirectory = just(config.eventStudioPath) if config.eventStudioPath else findEventStudioVSCodePath(
            os.path.expanduser(config.vsCodeExtensions))
        eventStudio = eventStudioDirectory.map(lambda p: os.path.join(p, 'evstudio'))
    else:
        print('Unsupported platform')
        exit()

    commandLine = eventStudio.map(lambda p: str.format(config.eventStudioCommandLine, eventStudio=f'"{p}"'))
    if commandLine.hasValue:
        os.system(commandLine.value)
    else:
        print('Could not find EventStudio')
        exit()


# TODO: Add support for macOS
def findEventStudioVSCodePath(extensionsPath) -> Maybe[str]:
    return first(os.listdir(extensionsPath),
                 lambda x: os.path.basename(x).lower().startswith('eventhelix.eventstudio-')).map(
        lambda p: os.path.join(extensionsPath, p))