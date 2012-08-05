# Trace Log to Sequence Diagram Conversion

Browsing through the code traces is an exercise in frustration. Applications produce hugh logs that take
hours to analyze. The Python scripts presented here let you visualize the traces as sequence diagrams. Interactions
between objects are presented visually.

## Tutorial: Sample Trace to Sequence Diagram Conversion

Let's get started by converting a sample trace into a sequence diagram. We start with downloading a few tools:

1. Download and install  a free 45 day trial of [EventStudio System Designer](http://www.EventHelix.com/EventStudio).
1. Download and install [Python 2.7](http://www.python.org/getit/releases/2.7/)
1. Download and extract the [trace to sequence diagram Python scripts](https://github.com/eventhelix/trace-to-sequence-diagram)
   * Click the [ZIP](https://github.com/eventhelix/trace-to-sequence-diagram/zipball/master) button to download files.
   * Alternatively click the "Clone in Windows" button. This would require downloading [GitHub for Windows](http://windows.github.com/)
1. Type cmd in the Run menu to invoke the Windows command prompt.
1. Navigate to the directory where to downloaded the Python scripts for this project.
1. On the command line now type:

	**trace2sequence.py -i sample_trace.txt**  

1. Click on the following generated diagrams:
	* **sequence-diagram.pdf** - A sequence diagram showing object level interations
	* **component-level-sequence-diagram.pdf** - A high level sequence diagram that shows high level interactions
	* **context-diagram.pdf** - A context diagram of the object interactions.
	* **xml-export.xml** - XML representation of the object interactions. Use this XML output to develop your custom tools.

