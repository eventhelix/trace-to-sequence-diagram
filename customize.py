"""
.. automodule:: customize
   :platform: Windows
   :synopsis: Customize the regular expressions that map to different elements
              of the sequence diagram.

.. moduleauthor:: EventHelix.com Inc.

"""
from collections import OrderedDict

# The trace messages follow this high level format. The current regular expression
# assumes that all traces are of the format:
#
# [time][generator][file]type body
#
# time:         The trace begins with time information in square brackets
#
# generator     Entity generating the trace message. This may be a generic entity name.
#               For C++ methods use the calling objects class name. For C functions
#               the C function generating the trace would be mentioned here.
#
# file          The next square bracket contains filename, line number information.
#
# type          Defines the type of a trace. The type here is used to determine the
#               mapping to an FDL statement. Refer to the traceMapper dictionary.
#               traceMapper maps the type to the trace handler that will parse the
#               trace body and extract information for generating an FDL statement.
#
# body          This is the text following the type statement. Parsing of this text
#               depends upon the type of the trace. This file contains the regular
#               expression definitions for parsing of the body for different
#               trace types.

traceRegex = r'\[(?P<time>.*)\]\s*\[(?P<generator>.*)\]\[(?P<file>.*)\]\s*(?P<type>\S+)\s+(?P<body>.*)'

# Map the type of the trace to the trace handler that will parse the trace body and
# extract the information needed for generating an FDL statement.
traceMapper = {
    'received': 'MessageReceive',
    'sent': 'MessageSent',
    'called': 'MethodInvoke',
    'returned': 'MethodReturn',
    'state': 'StateChange',
    'created': 'CreateObject',
    'deleted': 'DeleteObject',
    'begun': 'BeginAction',
    'ended': 'EndAction',
    'started': 'StartTimer',
    'stopped': 'StopTimer',
    'expired': 'ExpiredTimer',
    'allocated': 'AllocatedResource',
    'freed': 'FreedResource'
}

# The the trace type defaults to action if it is not found in the traceMapper
# dictionary.
defaultMapping = 'Action'

# === Statement regular expression and template definitions ===
# This section describes regular expressions that extract the trace information
# that is needed to define the FDL statements.
# You will see that the trace extraction regular expressions and the FDL statement
# generation templates are defined to next to each other. You would rarely need to
# change the FDL generation templates but they give you a context for defining the
# regular expressions.

# Regular expression for parsing the trace body when a message is being received
messageRxRegex = r'(?P<message>\w+)\s*(\((?P<params>.*)\))?\s*from\s*(?P<source>\w+)'

# Regular expression for parsing the trace body when a message is being sent
messageTxRegex = r'(?P<message>\w+)\s*(\((?P<params>.*)\))?\s*to\s*(?P<destination>\w+)'

# FDL mapping template for messages (received and sent messages)
messageTemplate = r'"{message}" {params} :"{source}" -> "{destination}"'

# Regular expression for parsing C++ method trace body. Trace body with :: is assumed
# to be a C++ method.
invokeMethodRegex = r'(?P<called>\w+)(\.|::)(?P<method>\w+)\s*(\((?P<params>\w+)\))?'

# Regular expression for parsing C function trace body. Trace body without :: is assumed
# to be a C function
invokeFunctionRegex = r'(?P<method>\w+)\s*(\((?P<params>\w+)\))?'

# FDL mapping template for function/method entry. 
invokeTemplate = r'"{caller}" invokes "{called}".{method}{params}'

# Regular expression for parsing the C++ method exit trace body.Trace body with :: is assumed
# to be a C++ method return
methodReturnRegex = r'(\((?P<params>.*)\))?\s*from\s*(?P<called>\w+)(\.|::)(?P<method>\w+)'

# Regular expression for parsing the C function exit trace body.Trace body without :: is assumed
# to be a C method return
functionReturnRegex = r'(\((?P<params>.*)\))?\s*from\s*(?P<method>\w+)'

# FDL mapping template for function/method exit
returnTemplate = r'"{called}".{method} returns {params}'

# Regular expression for parsing the object creation trace body
createRegex = r'(?P<created>\w+)\s*(\((?P<params>.*)\))?'

# FDL mapping template for object creation
createTemplate = r'"{creator}" creates "{created}"{params}'

# Regular expression for object deletion
deleteRegex = r'(?P<deleted>\w+)'

# FDL mapping template for object deletion
deleteTemplate = r'"{deletor}" deletes "{deleted}"'

# Any trace that does not map to a defined type is treated as an action trace.
# FDL mapping for action traces is defined here. The trace type is also
# included in the statement.
actionTemplate = r'"{actor}" action "{actionType} {action}"'

# FDL mapping template for state change trace body
stateChangeTemplate = r'"{object}" state = "{state}"'

# Regular expression for parsing the timer start, stop and expiry trace body.
timerRegex = r'(?P<timer>\w+)'

# FDL mapping templates for time start, stop and expiry traces.
startTimerTemplate = r'"{object}" starts {timer}'
stopTimerTemplate = r'"{object}" stops {timer}'
expiredTimerTemplate = r'timeout {timer}'

# FDL mapping for resource allocation and freeing traces.
allocateTemplate = r'"{object}" allocates "{resource}"'
freeTemplate = r'"{object}" frees "{resource}"'

# FDL mapping for action start and end traces.
beginActionTemplate = r'"{object}" begins action "{action}"'
endActionTemplate = r'"{object}" ends action "{action}"'

# Many statements contain parameters, They are parsed as attribute-value pairs.
# The attribute value pair separator and the attribute and value pair separator
# can be specified here. The default settings work for parameters of the form:
# attribute1 = value1, attribute2 = value2 etc.
attributeValueSeparator = '='
avpairSeparator = ','
paramTemplate = r'"{attribute}" = "{value}"'

# Specifies how the per statement remark has to be generated. By default the
# FDL remark contains the time and the file information (refer to traceRegex
# defined above).
remarkTemplate = r'|*{time} {file}*|'

# === OPTIONAL CUSTOMIZATION ===

# Add messages that need to be bookmarked in the PDF file. This is useful
# as it lets to quickly navigate through the sequence diagram output of
# a trace. PDF quick navigation bookmarks will be added whenever the messages
# listed below are seen in the trace message.
bookmarks = frozenset({
    'RandomAccessMessage',
    'RRCConnectionSetupComplete',
    'InitialUEMessage',
    'ReleaseConnection'
})

# FDL mapping template for the bookmarks
bookmarkTemplate = r'heading "{bookmark}"'

# === External entity definition ===
# EventStudio can generate a high level sequence diagram that can abstract
# out a set of classes as a high level entity. This abstraction is useful in
# understanding the trace output at a higher level of abstraction.
#
# List the interacting entities along with their parent. For example, the
# tuples below indicate that DSP_01 and DSP_23 belong to the same high level PHY entity.
# This means EventStudio will generate trace output at two levels:
# - A sequence diagram where DSP_01 and DSP_23 show up as separate axis.
# - A high level sequence diagram where PHY axis abstracts out the interactions
#   involving DSP_01 and DSP_23
# Just include the parent information for external actors in the system. Object parents
# for internal actors are extracted from the trace contents.
objectParents = OrderedDict([
    # Tuples of object and its parent
    # (entity, parent)

])
