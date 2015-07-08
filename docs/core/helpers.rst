Core Utilities
**************************

These modules provide various additional functionality the framework.

Settings
========================

.. module:: plc.core.settings
    :synopsis: Provides a helper class for saving and loading JSON
	       configuration files

.. autoclass:: Configuration

   This class provides a dictionary interface with two additional methods
   to assist in JSON-based persistence.

   `default_fn` is set to the first command-line argument, if it exists,
   otherwise ``"settings.json"``.

   .. method:: save(fn=default_fn)

   .. method:: load(fn=default_fn)

.. data:: conf

   The module provides access to this default configuration object, which
   will be loaded at import-time from the filename in the environment
   variable ``PLC_SETTINGS`` if that variable is present, otherwise from
   the ``default_fn``.

Persistence
===========================

.. module:: plc.core.persistence
   :synopsis: Provides an attribute-based persistent data store

.. autoclass:: PersistentData
    :members:
    :undoc-members:

    Values to be saved should be assigned as attributes.

Logging
=======================

.. module:: plc.core.logging
   :synopsis: Provides logging utilities that adapt based on the system
	      configuration

These functions will :func:`print` their arguments to a file or file
descriptor along with a timestamp, based on the logging configuration in
the default :data:`~.conf` object, if that exists, or else a built-in
default configuration.

.. function:: log(*args)

.. function:: debug(*args)

.. function:: warn(*args)

.. function:: error(*args)

.. function:: last_exception

   This convenience functiontion calls :func:`error` with the exception
   information and traceback from the last exception, formatted using
   the :mod:`traceback` module.
