"""
.. automodule:: config
   :platform: Windows
   :synopsis: Customize the regular expressions that map to different elements
              of the sequence diagram.

.. moduleauthor:: EventHelix.com Inc.

"""
# Specify the entity that generated the traces.
tracedEntity = 'RLC'

# Add messages that need to be bookmarked in the PDF file. This is useful
# as it lets to quickly navigate through the sequence diagram output of
# a trace. Note that bookmarks are defined as a set for efficient lookup.
bookmarks = {
    'RandomAccessMessage',
    'RRCConnectionSetupComplete',
    'InitialUEMessage',
    'ReleaseConnection'
}