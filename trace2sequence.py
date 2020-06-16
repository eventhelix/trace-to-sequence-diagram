#   This Source Code Form is subject to the terms of the Mozilla Public
#   License, v. 2.0. If a copy of the MPL was not distributed with this
#   file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
.. automodule:: trace2sequence
   :members:
   :platform:   Windows
   :synopsis:   This module performs the following tasks:
                (1) Read the log file and feed the individual lines into the
                trace parser.
                (2) The traces are mapped to statement objects using the regular
                expressions defined in customize.py. The parsed traces are stored as
                FDL statements.
                (3) FDL file is generated (trace.fdl).
                (4) EventStudio is invoked on the project.scn.json scenario project.
                    (project.scn.json references the newly generated trace.fdl).
.. moduleauthor:: EventHelix.com Inc.
"""

import argparse
import os
import re
import sys
from collections import OrderedDict

import config
import customize
import fdl

from funutils import Maybe, first, just


# utilities

def distinct(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


# trace parser

class TraceParser:
    """
    Parse trace lines and store parsed trace output.
    """

    def __init__(self):
        """
        Initialize the TraceParser object. The regular expression for tracing
        is also compiled at this time.
        """
        self.statementList = []
        self.objectDict = OrderedDict([])
        self.regex = re.compile(customize.traceRegex)
        self.attributes = {}
        self.usingDefaultComponent = False

    def parseTraceLine(self, line):
        """
        Parse a single line of trace and save the trace output.

        :param line: Trace line that needs to be parsed.
        """
        # Parse the line using the precompiled regular expression
        messageGroup = self.regex.search(line)
        if messageGroup is not None:
            self.attributes = messageGroup.groupdict()

            # The type named group parsed from the regular expression is used
            # to identify the function that will be parse the trace body
            traceType = self.attributes['type']
            if traceType in customize.traceMapper:
                traceBodyHandler = customize.traceMapper[traceType]
            else:
                traceBodyHandler = customize.defaultMapping

            traceBodyParser = fdl.traceHandlerMapper[traceBodyHandler]

            # Invoke the function to parse the body of the trace.
            statement = traceBodyParser(traceType, self.attributes['generator'], self.attributes['body'])

            # If trace parsing was successful, add a remark to the trace and then
            # save the parsed statement.
            if statement is not None:
                statement.attributeUpdate(self.attributes)
                self.saveStatement(statement)

    def saveStatement(self, statement):
        """
        Private method for saving a statement.

       :param statement: Statement object to be saved.
        """
        # Store the statement object
        self.statementList.append(statement)
        firstObj = None
        # In addition to saving the object also store the objects that
        # are being referenced inside an object dictionary. The object dictionary
        # will be used to generate the eternal and dynamic object statements
        # needed for FDL.
        # Note that the objects to be saved depend upon the type of the statement.
        # The entityList override of the statement is used to obtain this information
        for entity, entityType in statement.entityList():
            obj = statement.attributes[entity]
            if firstObj is None:
                firstObj = obj
            if obj in self.objectDict:
                if self.objectDict[obj] == 'any':
                    self.objectDict[obj] = entityType
            else:
                self.objectDict[obj] = entityType
            # Check if any object parent grouping is enabled. If it is enabled
            # check if any of the entities will need to define a default component
            if customize.objectParents and obj not in customize.objectParents:
                self.usingDefaultComponent = True


class Document:
    """
    The Document class generates the FDL file from the parsed statement information.
    """

    def __init__(self, traceParser, ofile):
        """
        Initialize the document dependencies.

        :param traceParser: The TraceParser object generated after parsing the
                            trace file.
        :param ofile: Output FDL file.
        """
        self.traceParser = traceParser
        self.ofile = ofile

    def generateDocument(self):
        """
        Generate the entire document, i.e. the header, body and the footer.
        """
        self.generateHeader()
        self.generateBody()
        self.generateFooter()

    @staticmethod
    def hasTypeChanged(previousType, nextType):
        """
        Private static method used when iterating over the object dictionary. The
        method takes the previous and the next type and determines if this represents
        a type change.
        :param previousType: The previous object type.
        :param nextType: The next object type
        :rvalue: True if a change is detected.
        """
        return previousType != '' and ((previousType == 'any' and 'dynamic' in nextType) or (
                'dynamic' in previousType and nextType == 'any'))

    @staticmethod
    def generateDeclaration(objType, entities):
        """
        Private method: Generate a declaration of by iterating over the objType.
        :param objType: String object type ('any' or 'dynamic'). 'any' will default
                        to eternal.
        :param entities: The object list that will be iterated over to identify the
                         statement.
        """
        declType = 'eternal' if objType == 'any' else 'dynamic'

        def createEntityWithParent(entity):
            """
            Create a string fragment of an object and its parent. This method is called to assemble the
            full declaration.
            :param entity: The entity for generating the fragment is passed as a parameter.
            :rvalue: string fragment for forming the complete declaration.
            """

            if customize.objectParents:
                parent = customize.objectParents.get(entity, 'Component')
                entityWithParent = '"{0}" in "{1}"'.format(entity, parent)
            else:
                entityWithParent = entity
            return entityWithParent

        entitiesWithParent = map(createEntityWithParent, entities)
        return declType + ': ' + ', '.join(entitiesWithParent) + '\n'

    @staticmethod
    def generateStyleAndTheme():
        retStr = ''

        if config.themeTemplate is not None:
            retStr += '#include <{0}.FDL>\n'.format(config.themeTemplate)

        retStr += '#include <stdinc.FDL>\n\n'

        return retStr

    def generateHeader(self):
        """
        Private method: Generate the FDL header
        """
        header = ''

        # Include the style and theme information
        header += self.generateStyleAndTheme()

        # Iterate over the object list and generate eternal and dynamic
        # declarations. The method generates a single declaration as long as it sees
        # objects of the same type. If the iterated object type changes, the method will
        # generate a new statement.
        entityList = []
        previousType = ''

        if customize.objectParents:
            parents = distinct(customize.objectParents.values())
            parentDeclaration = 'component: ' + ', '.join(['"' + parent + '"' for parent in parents]) + '\n'
            header += parentDeclaration

            if self.traceParser.usingDefaultComponent:
                header += 'component: "Component"\n'

        for obj, objtype in self.traceParser.objectDict.items():
            if Document.hasTypeChanged(previousType, objtype):
                header += self.generateDeclaration(previousType, entityList)
                entityList = []
            entityList.append(obj)
            previousType = objtype
        if len(entityList) != 0:
            header += self.generateDeclaration(previousType, entityList)

        # Generate the start of a feature block
        if config.themeTemplate is None:
            header += '\nfeature "generated flow" {\n'
        else:
            header += '\n{MyTheme} feature "generated flow" {\n'
        # The following code does an anonymous object create if an object delete
        # has been encountered in the trace but the object was already created
        # when tracing started. Such cases are flagged by a 'dynamic-deleted'
        # object type.
        for obj, objtype in self.traceParser.objectDict.items():
            if 'dynamic-deleted' in objtype:
                header += str.format('create {0}\n', obj)

        # Write the complete header to the file
        self.ofile.write(header)

    def checkAndGenerateBookmark(self, statement):
        """
        Private method. Traces to be bookmarked should be specified in customize.py file. A PDF bookmark
        should be generated if a trace segment matches the customize.py bookmark specification.
        This method checks and prefixes a bookmark.
        :param statement: Statement to be checked for a bookmark.
        """
        # Extract the bookmarking attribute. Proceed only if a bookmark attribute
        # is defined for the statement.
        bookmarkAttribute = statement.bookmarkAttribute()
        if bookmarkAttribute == '':
            return
        bookmarkText = statement.attributes[bookmarkAttribute]

        # If the bookmarking text is found, prefix the bookmark as heading statement
        if bookmarkText in customize.bookmarks:
            bookmarkStr = config.indent + str.format(customize.bookmarkTemplate, bookmark=bookmarkText) + '\n'
            self.ofile.write(bookmarkStr)

    def generateBody(self):
        """
        Private method. This method generates all the FDL file body by iterating
        over the statements extracted from the traces. Bookmarks are also generated
        from this method.
        """
        for statement in self.traceParser.statementList:
            fdlStatement = statement.generateStatement()
            self.checkAndGenerateBookmark(statement)
            self.ofile.write(fdlStatement)

    def generateFooter(self):
        """
        Private method. Generate the FDL footer.
        """
        self.ofile.write('}\n')


def parseCommandLine():
    """
    Parse the command line. Input and output file specification from the user are parsed.
    Help for the command-line is also supported.
    """
    parser = argparse.ArgumentParser(
        description='Convert traces to sequence diagrams via EventStudio',
        epilog='(c) EventHelix.com Inc. EventStudio customers are licensed to modify and use the script.')
    parser.add_argument('-i', '--input-file',
                        type=argparse.FileType('r'),
                        required=True,
                        help='input trace file (defaults to standard input)')
    parser.add_argument('-o', '--output-file',
                        type=argparse.FileType('w'),
                        default='trace.fdl',
                        help='Output file (defaults to trace.fdl - recommended)')
    return parser.parse_args()


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


def main():
    """
    Main body of the trace to sequence diagram script.
    """
    # Parse the traces
    args = parseCommandLine()
    traceParser = TraceParser()
    for line in args.input_file:
        traceParser.parseTraceLine(line)

    # Generate the FDL file
    doc = Document(traceParser, args.output_file)
    doc.generateDocument()
    args.output_file.close()

    # Generate the sequence diagram by invoking EventStudio from command-line
    generateOutputWithEventStudio()


# TODO: Add support for macOS
def findEventStudioVSCodePath(extensionsPath) -> Maybe[str]:
    return first(os.listdir(extensionsPath),
                 lambda x: os.path.basename(x).lower().startswith('eventhelix.eventstudio-')).map(
        lambda p: os.path.join(extensionsPath, p))


if __name__ == '__main__':
    main()
