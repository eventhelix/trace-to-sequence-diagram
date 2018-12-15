"""
.. automodule:: config
   :platform: Windows
   :synopsis: Configure the environment for running EventStudio.

.. moduleauthor:: EventHelix.com Inc.

"""

import os

# Path for identifying where the EventStudio executable is installed. Set to None
# if your wish to use the Visual Studio Code extension of EventStudio.
eventStudioPath = None

# Specifies the path where Visual Studio code extensions are installed in Windows
# (You do not need to change this unless your Visual Studio Code extensions are installed
# at a different path.)
vsCodeExtensions = r'%USERPROFILE%\.vscode\extensions'

# The EventStudio command line to be used to generate the sequence diagrams.
eventStudioCommandLine = r'{eventStudio} build project.scn.json'

# The indentation to be used in generating the FDL file.
indent = ' ' * 4

#theme template to use for generated sequence diagram. Set it to None to use
# the default theme. The available themes are:
# aqua, business, chocolate, pastel, rainbow, sunrise
themeTemplate = 'pastel'
