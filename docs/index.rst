.. plc documentation master file, created by
   sphinx-quickstart on Tue Jul  7 20:05:51 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PLC - Python Lighting Controls
************************************

Python Lighting Controls provides a server and various clients for
controlling lights over DMX with USB-DMX devices and the
:term:`Open Lighting Architecture`. The server currently understands groups
and cues, and will eventually support playback of those cues.

Get the Code
====================================

The source code is available on Github: https://github.com/baryon5/plc

:term:`PLC` uses the
`asyncio <https://docs.python.org/3/library/asyncio.html>`_ package new
in Python 3.4, as and such requires at least that version of python. It
also requires the :term:`OLA` Python bindings to be installed, which
unfortunately must be manually upgraded to support Python 3. (These
will require the python3-protobuf package). The `passlib` python 
package is also necessary.

Documentation
====================================

.. toctree::
   :maxdepth: 4
   :glob:
   :numbered:

   core/controller
   core/data
   core/advanced
   core/helpers
   
   network


* :ref:`genindex`
* :ref:`modindex`

