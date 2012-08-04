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
# a trace. Note that bookmarks are defined as a set for efficient lookup.
bookmarks = frozenset({
    'RandomAccessMessage',
    'RRCConnectionSetupComplete',
    'InitialUEMessage',
    'ReleaseConnection'
})

objectParents = OrderedDict([
    # Tuples of object and it's parent
    ('Mobile','UE'),
    ('DSP_01','PHY'),
    ('DSP_23','PHY'),
    ('RLC', 'BSC'),
    ('MessageRouter', 'BSC'),
    ('MobileManager', 'BSC'),
    ('CoreNetwork', 'EPC'),
    ('default-component', 'Component')
])
