# Trace Log to Sequence Diagram Conversion

Browsing through the code traces is an exercise in frustration. Applications produce hugh logs that take
hours to analyze. The Python scripts presented here let you visualize the traces as sequence diagrams. Interactions
between objects are presented visually.

## Step 1: Sample Trace to Sequence Diagram Conversion

Let's get started by converting a sample trace into a sequence diagram. We start with downloading a few tools:

1. Download and install  a free 45 day trial of [EventStudio System Designer](http://www.EventHelix.com/EventStudio).
1. Download and install [Python 2.7](http://www.python.org/getit/releases/2.7/)
1. Download and extract the [trace to sequence diagram Python scripts](https://github.com/eventhelix/trace-to-sequence-diagram)
   * Click the [ZIP](https://github.com/eventhelix/trace-to-sequence-diagram/zipball/master) button to download files.
   * Alternatively click the "Clone in Windows" button. This would require downloading [GitHub for Windows](http://windows.github.com/)
1. Before we proceed, please confirm the EventStudio path setting in the config.py file:
	* On machines running 64 bit Windows, the eventStudioPath Python variable should be set as:

		eventStudioPath=r'"C:\Program Files (x86)\EventHelix.com\EventStudio System Designer 5\evstudio.exe"'
	* On 32 bits Windows platforms, eventStudioPath should be set as:

		eventStudioPath=r'"C:\Program Files\EventHelix.com\EventStudio System Designer 5\evstudio.exe"'

		
1. Type cmd in the Run menu to invoke the Windows command prompt.
1. Navigate to the directory where to downloaded the Python scripts for this project.
1. On the command line now type:

	**trace2sequence.py -i sample_trace.txt**  

1. Click on the following generated diagrams:
	* **sequence-diagram.pdf** - A sequence diagram showing object level interations
	* **component-level-sequence-diagram.pdf** - A high level sequence diagram that shows high level interactions
	* **context-diagram.pdf** - A context diagram of the object interactions.
	* **xml-export.xml** - XML representation of the object interactions. Use this XML output to develop your custom tools.

## Step 2: Customize Regular Expressions to Map Traces to FDL (config.py)

By now you would have seen a sequence diagram generated from the sample trace output. If you can modify your traces to 
match the trace output in sample_trace.txt you can skip this step.

In most cases however, there will be changes needed in config.py to map your trace format to the FDL input needed by EventStudio.

The config.py file lets you configure the trace to sequence diagram (FDL) mapping for:
* Remarks that are shown on the right side of a sequence diagram
* Message interactions
* Method invoke and return
* Object creation and deletion
* Action taken by an object
* State transition
* Timer start, stop and expiry
* Resource allocation and freeing

We will be mapping traces to FDL statements to generate the sequence diagrams. The mapping will also require a basic understanding
of regular expressions. So lets visit these topics before we go any further.

### Learning FDL - The Sequence Diagram Markup Language

FDL (Feature Description Language) will be used to generate sequence diagrams. For a quick overview of FDL, refer to the
[FDL sequence diagram tutorial](http://www.eventhelix.com/EventStudio/sequence-diagram-tutorial.pdf).

### Python Regular Expressions

The Python website has a good [introduction to regular expressions](http://docs.python.org/library/re.html). [PythonRegEx.com](http://www.pythonregex.com/)
is great for testing your regular expressions.

### Templates and Regular Expressions

If you browse config.py, you will see that the trace extraction regular expressions and the FDL statement generation templates
are defined to next to each other. You would rarely need to change the FDL generation templates but they give you a context for
defining the regular expressions.

Refer to the example below. invokeRegex regular expression extracts named fields, called, method and params. These fields along
with the caller are used in the FDL template.

		# Regular expression for parsing the function/method entry trace body
		invokeRegex = '(?P<called>\w+)(\.|::)(?P<method>\w+)\s*(\((?P<params>\w+)\))?'

		# FDL mapping template for function/method entry
		invokeTemplate = '{caller} invokes {called}.{method}{params}'
