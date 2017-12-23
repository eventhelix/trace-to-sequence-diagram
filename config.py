"""
.. automodule:: config
   :platform: Windows
   :synopsis: Configure the environment for running EventStudio.

.. moduleauthor:: EventHelix.com Inc.

"""

# Path for identifying where the EventStudio execuable is installed.
eventStudioPath = r'"C:\Program Files (x86)\EventHelix.com\EventStudio System Designer 6\evstudio.exe"'

# The EventStudio command line to be used to generate the sequence diagrams.
eventStudioCommandLine = r'{eventStudio} build project.scn.json'

# The identation to be used in generating the FDL file.
indent = ' ' * 4

#style template to use for generated sequence diagram. Set it to None if
#you do not wish to use any styles
styleTemplate = r'#include "style-green-khakhi-modern.fdl"'

#theme template to use for generated sequence diagram. Set it to None if
#you do not wish to use any styles
themeTemplate = r'#include "theme-embedded.fdl"'
