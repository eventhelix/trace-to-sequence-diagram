"""
.. automodule:: config
   :platform: Windows
   :synopsis: Configure the environment for running EventStudio.

.. moduleauthor:: EventHelix.com Inc.

"""

import sys

# Path for identifying where the EventStudio executable is installed. Set to None
# for the script to find the EventStudio path from the installed vscode extension.
eventstudio_path = None

# Specifies the path where Visual Studio Code extensions are installed under Windows
# (You do not need to change this unless your Visual Studio Code extensions are installed
# at a different path.)

if sys.platform == 'win32':  # Windows
    vscode_extensions = r'%USERPROFILE%\.vscode\extensions'
elif sys.platform == 'darwin':  # macOS
    vscode_extensions = r'~/.vscode/extensions'


# The indentation to be used in generating the FDL file.
indent = ' ' * 4

# Theme template to use for generated sequence diagram. Set it to None to use
# the default theme. The available themes are:
# aqua, business, chocolate, pastel, rainbow, sunrise
theme_template = 'pastel'
