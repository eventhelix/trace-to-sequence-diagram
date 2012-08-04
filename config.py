"""
.. automodule:: config
   :platform: Windows
   :synopsis: Configure the regular expressions that map to different elements
              of the sequence diagram.

.. moduleauthor:: EventHelix.com Inc.

"""



# FDL mapping template for the bookmarks
bookmarkTemplate = 'heading "{bookmark}"'

# The trace messages follow this high level format. The current regular expression
# assumes that all traces are of the format:
# [time][file]type body
# time: the trace begins with time information in square brackets
# file: The next square bracket contains filename, line number information
# type: Defines the type of a trace. The type here is used to determine the
#       mapping to an FDL statement. Refer to the traceMapper dictionary in
#       fdl.py. This file maps the type to the a function that will handle
#       the parsing of the body.
# body: This is the text following the type statement. Parsing of this text
#       depends upon the type of the trace. This file contains the regular
#       expression definitions for parsing of the body for different
#       trace types.

traceRegex = '\[(?P<time>.*)\]\s*\[(?P<file>.*)\]\s*(?P<type>\S+)\s+(?P<body>.*)'

# Specifies how the per statement remark has to be generated. By default the
# FDL remark contains the time and the file information (refer to traceRegex
# defined above.
remarkTemplate = r'(* {time} {file} *)'

# Regular expression for parsing the trace body when a message is being received
messageRxRegex = '(?P<message>\w+)\s*(\((?P<params>.*)\))?\s*from\s*(?P<source>\w+)'

# Regular expression for parsing the trace body when a message is being sent
messageTxRegex = '(?P<message>\w+)\s*(\((?P<params>.*)\))?\s*to\s*(?P<destination>\w+)'

# FDL mapping template for messages (received and sent messages)
messageTemplate = '{message} {params} :{source} -> {destination}'

# Regular expression for parsing the function/method entry trace body
invokeRegex = '(?P<called>\w+)(\.|::)(?P<method>\w+)\s*(\((?P<params>\w+)\))?'

# FDL mapping template for function/method entry
invokeTemplate = '{caller} invokes {called}.{method}{params}'

# Regular expression for parsing the function/method exit trace body
returnRegex = '(\((?P<params>.*)\))?\s*from\s*(?P<called>\w+)(\.|::)(?P<method>\w+)'

# FDL mapping template for function/method exit
returnTemplate = '{called}.{method} returns {params}'

# Regular expression for parsing the object creation trace body
createRegex = '(?P<created>\w+)\s*(\((?P<params>.*)\))?'

# FDL mapping template for object creation
createTemplate = '{creator} creates {created}{params}'

# Regular expression for object deletion
deleteRegex = '(?P<deleted>\w+)'

# FDL mapping template for object deletion
deleteTemplate = '{deletor} deletes "{deleted}"'

# Any trace that does not map to a defined type is treated as an action trace.
# FDL mapping for action traces is defined here. The trace type is also
# included in the statement.
actionTemplate = '{actor} takes action "{actionType} {action}"'

# FDL mapping template for state change trace body
stateChangeTemplate = '{object} state = "{state}"'

# Regular expression for parsing the timer start, stop anmd expiry trace body.
timerRegex = '(?P<timer>\w+)'

# FDL mapping templates for time start, stop and expiry traces.
startTimerTemplate = '{object} starts {timer}'
stopTimerTemplate = '{object} stops {timer}'
expiredTimerTemplate = 'timeout {timer}'

# FDL mapping for resource allocation and freeing traces.
allocateTemplate = '{object} allocates "{resource}"'
freeTemplate = '{object} frees "{resource}"'

# FDL mapping for action start and end traces.
beginActionTemplate = '{object} begins action "{action}"'
endActionTemplate = '{object} ends action "{action}"'

# Many statements contain parameters, They are parsed as attribute-value pairs.
# The attribute value pair separator and the attribute and value pair sepeator
# can be specifield here. The default settings work for parameters of the form:
# attribute1 = value1, attribute2 = value2 etc.
attributeValueSeparator = '='
avpairSeparator = ','
paramTemplate = '"{attribute}" = "{value}"'

# Path for identifying where the EventStudio execuable is installed.
eventStudioPath=r'"C:\Program Files (x86)\EventHelix.com\EventStudio System Designer 5\evstudio.exe"'

# The EventStudio command line to be used to generate the sequence diagrams.
eventStudioCommandLine = r'{eventStudio} TraceProject.scn /GenerateAll'

# The identation to be used in generating the FDL file.
indent = ' '*4

#style template to use for generated sequence diagram. Set it to None if
#you do not wish to use any styles
styleTemplate = r'#include "style-green-khakhi-modern.fdl"'

#theme template to use for generated sequence diagram. Set it to None if
#you do not wish to use any styles
themeTemplate = r'#include "theme-embedded.fdl"'
