"""
.. automodule:: config
   :platform: Windows
   :synopsis: Configure the environment for running EventStudio.

.. moduleauthor:: EventHelix.com Inc.

"""

import os

# Path for identifying where the EventStudio executable is installed. Set to None
# for the script to find the EventStudio path from the installed vscode extension.
eventStudioPath = None

# Specifies the path where Visual Studio code extensions are installed in Windows
# (You do not need to change this unless your Visual Studio Code extensions are installed
# at a different path.)
vsCodeExtensions = r'%USERPROFILE%\.vscode\extensions'

# The EventStudio command line to be used to generate the sequence diagrams.
eventStudioCommandLine = r'{eventStudio} build project.scn.json'

# The indentation to be used in generating the FDL file.
indent = ' ' * 4

# Theme template to use for generated sequence diagram. Set it to None to use
# the default theme. The available themes are:
# aqua, business, chocolate, pastel, rainbow, sunrise
themeTemplate = 'pastel'
