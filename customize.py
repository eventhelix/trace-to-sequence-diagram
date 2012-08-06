"""
.. automodule:: config
   :platform: Windows
   :synopsis: Customize the regular expressions that map to different elements
              of the sequence diagram.

.. moduleauthor:: EventHelix.com Inc.

"""
from collections import OrderedDict

# Specify the entity that generated the traces.
tracedEntity = 'RLC'

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
objectParents = OrderedDict([
    # Tuples of object and its parent
    # (entity, parent)
    ('Mobile','UE'),
    ('DSP_01','PHY'),
    ('DSP_23','PHY'),
    ('RLC', 'BSC'),
    ('MessageRouter', 'BSC'),
    ('MobileManager', 'BSC'),
    ('CoreNetwork', 'EPC'),
    ('default-component', 'Component')
])
