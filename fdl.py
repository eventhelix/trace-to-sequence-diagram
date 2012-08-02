"""
.. automodule:: fdl
   :members:
   :platform: Windows
   :synopsis: Utilities and classes needed for trace to FDL generation.
.. moduleauthor:: EventHelix.com Inc.
"""

import re
import config
from collections import OrderedDict

def trimSplit(s, sep):
    """
    Take a string and split it across the separator.

    :param s: string to be split
    :param sep: separator to be used for splitting
    :rtype: tuple of strings (extra blank spaces are removed)
    """
    if sep in s:
        s1,s2 = s.split(sep)
        return s1.strip(), s2.strip()
    else:
        return '',''

def formatParams(paramString):
    """
    Parse the format string, reformat it and store it as a valid parameter string
    for FDL. The parameters are enclosed in paranthesis. An empty string is
    returned if no valid parameters are found.

    :param paramString: Raw parameter string extracted from the traces.
    :rtype: string that is suitable for FDL statements.
    """
    avPairStr = ''
    if paramString != None and len(paramString) != 0 and config.attributeValueSeparator in paramString:
        avPairStr = '('
        avpairList = [trimSplit(item, config.attributeValueSeparator) for item in paramString.split(config.avpairSeparator)]
        for att,val in avpairList:
            avPairStr += str.format(config.paramTemplate, attribute=att, value=val)
            avPairStr += ','
        avPairStr = avPairStr[:-1]
        avPairStr += ')'
    return avPairStr

class Stack:
    """
    A class used to keep track of method invocations seen in the traces.
    """
    def __init__(self):
        """
        Initialize the stack.
        """
        self.stack = []

    def push(self, item):
        """
        Push an item on to the stack.
        """
        self.stack.append(item)

    def pop(self):
        """
        Pop an item from the stack.
        """
        return self.stack.pop()

    def top(self):
        """
        Get the item at the top of the stack.
        """
        return self.stack[-1]

    def length(self):
        """
        Get the stack length.
        """
        return len(self.stack)

    def currentObject(self):
        """
        Return the currently active object. If no object is present on the
        stack, the default object defined in traceEntity in the config.py fi;e
        is returned.

        :rtype: string name of the currently active object.
        """
        if self.length() != 0:
            return self.top().attributes['called']
        else:
            return config.tracedEntity

# Stack object rebuilds the stack from the trace messages.
stack = Stack()

class Statement:
    """
    Base class for representing FDL statements.
    """
    def __init__(self):
        self.attributes = {}
        self.remarks = ''


    def convertToFDL(self):
        """
        This method should be overriden to return a FDL statement that is derived
        from the trace body.
        """
        return ''

    def entityList(self):
        """
        Override this method to return a list containing the entities derived
        from the trace command. For example, a message list will return two
        entiries while an action statement will return one entity.
        """
        return []

    def bookmarkAttribute(self):
        """
        Override this method to return a string that should be compared with the
        config.py file's bookmarks. If the string returned by this method
        is contained in the config.py's bookmarks, a bookmark entry will be
        generated in the PDF sequence diagram.
        """
        return ''

    def generateStatement(self):
        """
        This method generates the complete FDL statement. The string for the FDL
        as well as a remark is included in the string.

        :rvalue: string containing the complete FDL statement (including the
                 correct indentation and the remark.
        """
        fdlText = config.indent + self.convertToFDL() + '\n'+ config.indent
        fdlText += self.remarks + '\n\n'
        return fdlText

class MessageStatement(Statement):
    """
    Represents the FDL message statement. This class is used in message sent and
    receive processing.
    """
    def convertToFDL(self):
        return str.format(config.messageTemplate, **self.attributes)

    def entityList(self):
        return [('source','any'),('destination','any')]

    def bookmarkAttribute(self):
        return 'message'

# Compile the regular expression for received message extraction from the trace body.
messageReceiveRegex = re.compile(config.messageRxRegex)

def MessageReceive(traceType, traceText):
    """
    Parse the traceText from a message receive trace and return a statement object.
    The raw string trace body is parsed into a message statement object with the help
    of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    messageGroup = messageReceiveRegex.search(traceText)
    if messageGroup != None:
         statement = MessageStatement()
         statement.attributes = messageGroup.groupdict()
         statement.attributes['destination'] = stack.currentObject()
         if 'params' in statement.attributes:
            statement.attributes['params'] = formatParams(statement.attributes['params'])
    return statement

messageSentRegex = re.compile(config.messageTxRegex)
def MessageSent(traceType, traceText):
    """
    Parse the traceText from a message sent trace and return a statement object.
    The raw string trace body is parsed into a message statement object with the help
    of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    messageGroup = messageSentRegex.search(traceText)
    if messageGroup != None:
         statement = MessageStatement()
         statement.attributes = messageGroup.groupdict()
         statement.attributes['source'] = stack.currentObject()
         if 'params' in statement.attributes:
            statement.attributes['params'] = formatParams(statement.attributes['params'])
    return statement

class InvokeStatement(Statement):
    """
    Represents the FDL method invoke statement.
    """
    def convertToFDL(self):
        return str.format(config.invokeTemplate, **self.attributes)

    def entityList(self):
        return [('caller','any'),('called', 'any')]

    def bookmarkAttribute(self):
        return 'method'

invokeRegex = re.compile(config.invokeRegex)
def MethodInvoke(traceType, traceText):
    """
    Parse the traceText of a method invoke and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    invokeGroup = invokeRegex.search(traceText)
    if invokeGroup != None:
        statement = InvokeStatement()
        statement.attributes = invokeGroup.groupdict()
        statement.attributes['caller'] = stack.currentObject()
        if 'params' in statement.attributes:
            statement.attributes['params'] = formatParams(statement.attributes['params'])
        stack.push(statement)
    return statement

class ReturnStatement(Statement):
    """
    Represents the FDL method return statement.
    """
    def convertToFDL(self):
        return str.format(config.returnTemplate, **self.attributes)

    def entityList(self):
        return [('called','any')]

returnRegex = re.compile(config.returnRegex)
def MethodReturn(traceType, traceText):
    """
    Parse the traceText of a "method return" and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    if stack.length() != 0:
        methodStatement = stack.pop()
        returnGroup = returnRegex.search(traceText)
        if returnGroup != None:
            statement = ReturnStatement()
            statement.attributes = returnGroup.groupdict()
            if 'params' in statement.attributes:
                statement.attributes['params'] = formatParams(statement.attributes['params'])
    return statement


class CreateStatement(Statement):
    """
    Represents the FDL object create statement.
    """
    def convertToFDL(self):
        return str.format(config.createTemplate, **self.attributes)

    def entityList(self):
        return [('creator','any'), ('created', 'dynamic-created')]

createRegex = re.compile(config.createRegex)
def CreateObject(traceType, traceText):
    """
    Parse the traceText of an object create and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    createGroup = createRegex.search(traceText)
    if createGroup != None:
        statement = CreateStatement()
        statement.attributes = createGroup.groupdict()
        statement.attributes['creator'] = stack.currentObject()
        if 'params' in statement.attributes:
            statement.attributes['params'] = formatParams(statement.attributes['params'])
    return statement

class DeleteStatement(Statement):
    """
    Represents the FDL object delete statement.
    """
    def convertToFDL(self):
        return str.format(config.deleteTemplate, **self.attributes)

    def entityList(self):
        return [('deletor','any'), ('deleted', 'dynamic-deleted')]

deleteRegex = re.compile(config.deleteRegex)
def DeleteObject(traceType, traceText):
    """
    Parse the traceText of an object delete and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    deleteGroup = deleteRegex.search(traceText)
    if deleteGroup != None:
        statement = DeleteStatement()
        statement.attributes = deleteGroup.groupdict()
        statement.attributes['deletor'] = stack.currentObject()
    return statement

timerRegex = re.compile(config.timerRegex)

class TimerStatement(Statement):
    """
    Represents the FDL timer statements. This class acts as the base class for
    all the timer management statements.
    """
    def bookmarkAttribute(self):
        return 'timer'

class StartTimerStatement(TimerStatement):
    """
    Represents FDL timer start.
    """
    def convertToFDL(self):
        return str.format(config.startTimerTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

def StartTimer(traceType, traceText):
    """
    Parse the traceText of a timer start and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    timerGroup = timerRegex.search(traceText)
    if timerGroup != None:
        statement = StartTimerStatement()
        statement.attributes['object'] = stack.currentObject()
        statement.attributes['timer'] = traceText.strip()
    return statement

class StopTimerStatement(TimerStatement):
    """
    Represents FDL stop statement.
    """
    def convertToFDL(self):
        return str.format(config.stopTimerTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

def StopTimer(traceType, traceText):
    """
    Parse the traceText of a timer stop and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    timerGroup = timerRegex.search(traceText)
    if timerGroup != None:
        statement = StopTimerStatement()
        statement.attributes['object'] = stack.currentObject()
        statement.attributes['timer'] = traceText.strip()
    return statement

class ExpiredTimerStatement(TimerStatement):
    """
    Represents FDL timeout statement.
    """
    def convertToFDL(self):
        return str.format(config.expiredTimerTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

def ExpiredTimer(traceType, traceText):
    """
    Parse the traceText of a timer expiry and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    timerGroup = timerRegex.search(traceText)
    if timerGroup != None:
        statement = ExpiredTimerStatement()
        statement.attributes['object'] = stack.currentObject()
        statement.attributes['timer'] = traceText.strip()
    return statement

class ActionStatement(Statement):
    """
    Represents the FDL action statement.
    """
    def convertToFDL(self):
        return str.format(config.actionTemplate, **self.attributes)

    def entityList(self):
        return [('actor','any')]

    def bookmarkAttribute(self):
        return 'action'


def Action(traceType, traceText):
    """
    Parse the traceText of any action and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = ActionStatement()
    statement.attributes['actor'] = stack.currentObject()
    statement.attributes['actionType'] = traceType
    statement.attributes['action'] = traceText.strip()
    return statement

class StateChangeStatement(Statement):
    """
    Represents the FDL state change statement.
    """
    def convertToFDL(self):
        return str.format(config.stateChangeTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

    def bookmarkAttribute(self):
        return 'state'

def StateChange(traceType, traceText):
    """
    Parse the traceText of a state change and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = StateChangeStatement()
    statement.attributes['object'] = stack.currentObject()
    statement.attributes['state'] = traceText.strip()
    return statement


class AllocateStatement(Statement):
    """
    Represents the resource allocation FDL statement.
    """
    def convertToFDL(self):
        return str.format(config.allocateTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

    def bookmarkAttribute(self):
        return 'resource'

def AllocatedResource(traceType, traceText):
    """
    Parse the traceText of a resource allocation and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = AllocateStatement()
    statement.attributes['object'] = stack.currentObject()
    statement.attributes['resource'] = traceText.strip()
    return statement

class FreeStatement(Statement):
    """
    Represents the resource free FDL statement.
    """
    def convertToFDL(self):
        return str.format(config.freeTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

    def bookmarkAttribute(self):
        return 'resource'

def FreedResource(traceType, traceText):
    """
    Parse the traceText of a resource free trace and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = FreeStatement()
    statement.attributes['object'] = stack.currentObject()
    statement.attributes['resource'] = traceText.strip()
    return statement

class BeginActionStatement(Statement):
    """
    Represent an action start FDL statement.
    """
    def convertToFDL(self):
        return str.format(config.beginActionTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

    def bookmarkAttribute(self):
        return 'action'

def BeginAction(traceType, traceText):
    """
    Parse the traceText of an action start trace and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = BeginActionStatement()
    statement.attributes['object'] = stack.currentObject()
    statement.attributes['action'] = traceText.strip()
    return statement

class EndActionStatement(Statement):
    """
    Represents the action end FDL statement.
    """
    def convertToFDL(self):
        return str.format(config.endActionTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

    def bookmarkAttribute(self):
        return 'action'

def EndAction(traceType, traceText):
    """
    Parse the traceText of an end action and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in config.py file.

    :param traceType: string containing the trace type
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = EndActionStatement()
    statement.attributes['object'] = stack.currentObject()
    statement.attributes['action'] = traceText.strip()
    return statement

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
#
#       The following dictionary maps the trace type to a function that will
#       extract the FDL statement from the message body.

traceMapper = {
   'received'   :   MessageReceive,
   'sent'       :   MessageSent,
   'called'     :   MethodInvoke,
   'returned'   :   MethodReturn,
   'state'   :      StateChange,
   'created'    :   CreateObject,
   'deleted'    :   DeleteObject,
   'begun'      :   BeginAction,
   'ended'      :   EndAction,
   'started'    :   StartTimer,
   'stopped'    :   StopTimer,
   'expired'    :   ExpiredTimer,
   'allocated'  :   AllocatedResource,
   'freed'      :   FreedResource
}

# The the trace type defaults to action if it is not found in the traceMapper
# dictionary.

defaultMapping = Action