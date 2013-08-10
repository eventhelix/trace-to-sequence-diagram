"""
.. automodule:: fdl
   :members:
   :platform: Windows
   :synopsis: Utilities and classes needed for trace to FDL generation.
.. moduleauthor:: EventHelix.com Inc.
"""

import re
import config
import customize
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
    if paramString != None and len(paramString) != 0 and customize.attributeValueSeparator in paramString:
        avPairStr = '('
        avpairList = [trimSplit(item, customize.attributeValueSeparator) for item in paramString.split(customize.avpairSeparator)]
        for att,val in avpairList:
            avPairStr += str.format(customize.paramTemplate, attribute=att, value=val)
            avPairStr += ','
        avPairStr = avPairStr[:-1]
        avPairStr += ')'
    return avPairStr


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
        entries while an action statement will return one entity.
        """
        return []

    def bookmarkAttribute(self):
        """
        Override this method to return a string that should be compared with the
        customize.py file's bookmarks. If the string returned by this method
        is contained in the customize.py's bookmarks, a bookmark entry will be
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

    def attributeUpdate(self, traceAttributes):
        """
        This method is called when the messages are being parsed. The statement object
        extracts the relevant attributes from this method.
        :param traceAttributes: List of attributes extracted from the trace.
        """
        self.remarks = str.format(customize.remarkTemplate, **traceAttributes)




class MessageStatement(Statement):
    """
    Represents the FDL message statement. This class is used in message sent and
    receive processing.
    """
    def convertToFDL(self):
        return str.format(customize.messageTemplate, **self.attributes)

    def bookmarkAttribute(self):
        return 'message'

class MessageReceiveStatement(MessageStatement):

    def entityList(self):
        return [('destination','any'),('source','any')]

# Compile the regular expression for received message extraction from the trace body.
messageReceiveRegex = re.compile(customize.messageRxRegex)

def MessageReceive(traceType, traceGenerator, traceText):
    """
    Parse the traceText from a message receive trace and return a statement object.
    The raw string trace body is parsed into a message statement object with the help
    of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    messageGroup = messageReceiveRegex.search(traceText)
    if messageGroup != None:
         statement = MessageReceiveStatement()
         statement.attributes = messageGroup.groupdict()
         statement.attributes['destination'] = traceGenerator
         if 'params' in statement.attributes:
            statement.attributes['params'] = formatParams(statement.attributes['params'])
    return statement

class MessageSendStatement(MessageStatement):

    def entityList(self):
        return [('source','any'),('destination','any')]

messageSentRegex = re.compile(customize.messageTxRegex)
def MessageSent(traceType, traceGenerator, traceText):
    """
    Parse the traceText from a message sent trace and return a statement object.
    The raw string trace body is parsed into a message statement object with the help
    of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    messageGroup = messageSentRegex.search(traceText)
    if messageGroup != None:
         statement = MessageSendStatement()
         statement.attributes = messageGroup.groupdict()
         statement.attributes['source'] = traceGenerator
         if 'params' in statement.attributes:
            statement.attributes['params'] = formatParams(statement.attributes['params'])
    return statement

class InvokeStatement(Statement):
    """
    Represents the FDL method invoke statement.
    """
    def convertToFDL(self):
        return str.format(customize.invokeTemplate, **self.attributes)

    def entityList(self):
        return [('called','any'),('caller', 'any')]

    def bookmarkAttribute(self):
        return 'method'

invokeRegex = re.compile(customize.invokeRegex)
def MethodInvoke(traceType, traceGenerator, traceText):
    """
    Parse the traceText of a method invoke and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    if '::'  in traceText:
        # C++ method trace
        invokeGroup = invokeMethodRegex.search(traceText)
        statement.attributes = invokeGroup.groupdict()
    else:
        # c function trace
        invokeGroup = invokeFunctionRegex.search(traceText)
        statement.attributes = invokeGroup.groupdict()
        # FDL requires an object name and method name. In C functions
        # the function name (designated as method) is also used as
        # the called object name
        statement.attributes['called'] = statement.attributes['method']

    if invokeGroup != None:
        statement = InvokeStatement()
        statement.attributes['caller'] = traceGenerator
        if 'params' in statement.attributes:
            statement.attributes['params'] = formatParams(statement.attributes['params'])
    return statement

class ReturnStatement(Statement):
    """
    Represents the FDL method return statement.
    """
    def convertToFDL(self):
        return str.format(customize.returnTemplate, **self.attributes)

    def entityList(self):
        return [('called','any')]

returnRegex = re.compile(customize.returnRegex)
def MethodReturn(traceType, traceGenerator, traceText):
    """
    Parse the traceText of a "method return" and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
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
        return str.format(customize.createTemplate, **self.attributes)

    def entityList(self):
        return [('creator','any'), ('created', 'dynamic-created')]

createRegex = re.compile(customize.createRegex)
def CreateObject(traceType, traceGenerator, traceText):
    """
    Parse the traceText of an object create and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    createGroup = createRegex.search(traceText)
    if createGroup != None:
        statement = CreateStatement()
        statement.attributes = createGroup.groupdict()
        statement.attributes['creator'] = traceGenerator
        if 'params' in statement.attributes:
            statement.attributes['params'] = formatParams(statement.attributes['params'])
    return statement

class DeleteStatement(Statement):
    """
    Represents the FDL object delete statement.
    """
    def convertToFDL(self):
        return str.format(customize.deleteTemplate, **self.attributes)

    def entityList(self):
        return [('deletor','any'), ('deleted', 'dynamic-deleted')]

deleteRegex = re.compile(customize.deleteRegex)
def DeleteObject(traceType, traceGenerator, traceText):
    """
    Parse the traceText of an object delete and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    deleteGroup = deleteRegex.search(traceText)
    if deleteGroup != None:
        statement = DeleteStatement()
        statement.attributes = deleteGroup.groupdict()
        statement.attributes['deletor'] = traceGenerator
    return statement

timerRegex = re.compile(customize.timerRegex)

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
        return str.format(customize.startTimerTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

def StartTimer(traceType, traceGenerator, traceText):
    """
    Parse the traceText of a timer start and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    timerGroup = timerRegex.search(traceText)
    if timerGroup != None:
        statement = StartTimerStatement()
        statement.attributes['object'] = traceGenerator
        statement.attributes['timer'] = traceText.strip()
    return statement

class StopTimerStatement(TimerStatement):
    """
    Represents FDL stop statement.
    """
    def convertToFDL(self):
        return str.format(customize.stopTimerTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

def StopTimer(traceType, traceGenerator, traceText):
    """
    Parse the traceText of a timer stop and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    timerGroup = timerRegex.search(traceText)
    if timerGroup != None:
        statement = StopTimerStatement()
        statement.attributes['object'] = traceGenerator
        statement.attributes['timer'] = traceText.strip()
    return statement

class ExpiredTimerStatement(TimerStatement):
    """
    Represents FDL timeout statement.
    """
    def convertToFDL(self):
        return str.format(customize.expiredTimerTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

def ExpiredTimer(traceType, traceGenerator, traceText):
    """
    Parse the traceText of a timer expiry and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = None
    timerGroup = timerRegex.search(traceText)
    if timerGroup != None:
        statement = ExpiredTimerStatement()
        statement.attributes['object'] = traceGenerator
        statement.attributes['timer'] = traceText.strip()
    return statement

class ActionStatement(Statement):
    """
    Represents the FDL action statement.
    """
    def convertToFDL(self):
        return str.format(customize.actionTemplate, **self.attributes)

    def entityList(self):
        return [('actor','any')]

    def bookmarkAttribute(self):
        return 'action'


def Action(traceType, traceGenerator, traceText):
    """
    Parse the traceText of any action and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = ActionStatement()
    statement.attributes['actor'] = traceGenerator
    statement.attributes['actionType'] = traceType
    statement.attributes['action'] = traceText.strip()
    return statement

class StateChangeStatement(Statement):
    """
    Represents the FDL state change statement.
    """
    def convertToFDL(self):
        return str.format(customize.stateChangeTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

    def bookmarkAttribute(self):
        return 'state'

def StateChange(traceType, traceGenerator, traceText):
    """
    Parse the traceText of a state change and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = StateChangeStatement()
    statement.attributes['object'] = traceGenerator
    statement.attributes['state'] = traceText.strip()
    return statement


class AllocateStatement(Statement):
    """
    Represents the resource allocation FDL statement.
    """
    def convertToFDL(self):
        return str.format(customize.allocateTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

    def bookmarkAttribute(self):
        return 'resource'

def AllocatedResource(traceType, traceGenerator, traceText):
    """
    Parse the traceText of a resource allocation and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = AllocateStatement()
    statement.attributes['object'] = traceGenerator
    statement.attributes['resource'] = traceText.strip()
    return statement

class FreeStatement(Statement):
    """
    Represents the resource free FDL statement.
    """
    def convertToFDL(self):
        return str.format(customize.freeTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

    def bookmarkAttribute(self):
        return 'resource'

def FreedResource(traceType, traceGenerator, traceText):
    """
    Parse the traceText of a resource free trace and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = FreeStatement()
    statement.attributes['object'] = traceGenerator
    statement.attributes['resource'] = traceText.strip()
    return statement

class BeginActionStatement(Statement):
    """
    Represent an action start FDL statement.
    """
    def convertToFDL(self):
        return str.format(customize.beginActionTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

    def bookmarkAttribute(self):
        return 'action'

def BeginAction(traceType, traceGenerator, traceText):
    """
    Parse the traceText of an action start trace and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = BeginActionStatement()
    statement.attributes['object'] = traceGenerator
    statement.attributes['action'] = traceText.strip()
    return statement

class EndActionStatement(Statement):
    """
    Represents the action end FDL statement.
    """
    def convertToFDL(self):
        return str.format(customize.endActionTemplate, **self.attributes)

    def entityList(self):
        return [('object','any')]

    def bookmarkAttribute(self):
        return 'action'

def EndAction(traceType, traceGenerator, traceText):
    """
    Parse the traceText of an end action and return a statement object.
    The raw string trace body is parsed into a message statement object with the
    help of the regular expression defined in customize.py file.

    :param traceType: string containing the trace type
    :param traceGenerator: object generating the trace
    :param traceText: string containing the raw trace body
    :rtype: statement object containing information about the trace.
    """
    statement = EndActionStatement()
    statement.attributes['object'] = traceGenerator
    statement.attributes['action'] = traceText.strip()
    return statement


# trace string to the handler mapping is a two step process. The user type string gets mapped
# to trace handler string in customize.fdl. The second step is mapping the trace handler string
# to trace handler function.

traceHandlerMapper = {
   'MessageReceive'     :   MessageReceive,
   'MessageSent'        :   MessageSent,
   'MethodInvoke'       :   MethodInvoke,
   'MethodReturn'       :   MethodReturn,
   'StateChange'        :   StateChange,
   'CreateObject'       :   CreateObject,
   'DeleteObject'       :   DeleteObject,
   'BeginAction'        :   BeginAction,
   'EndAction'          :   EndAction,
   'StartTimer'         :   StartTimer,
   'StopTimer'          :   StopTimer,
   'ExpiredTimer'       :   ExpiredTimer,
   'AllocatedResource'  :   AllocatedResource,
   'FreedResource'      :   FreedResource,
   'Action'             :   Action
}

