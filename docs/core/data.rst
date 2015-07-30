Entities
********************

.. module:: plc.core.data
   :synopsis: PLC lighting entities

.. autoclass:: Registry
	      
   A :class:`Registry` is a dictionary of objects of the class it was created
   for. It also contains internal methods for persistence in binary form
   with the help of a :class:`.PersistentData` object.

   .. automethod:: new

      This convenience function will create a new object of the class
      associated with the :class:`Registry` and automatically add it.

Both the :class:`Cue` and :class:`Group` classes inherit from
:class:`DimmerGroup` and share much of the same functionality. When
assigning group or channel levels for these classes, the levels should always
be fractions of 1.

.. autoclass:: DimmerGroup

   .. method:: get_dimmers(level=None)
      
      This method will return a dictionary of dimmers that should be
      affected by this :class:`DimmerGroup`, with any channels set in the
      group completely overriding any dimmer levels gathered from nested
      groups, which will also have their levels updated.

      ``level`` should be a fraction of 1, and will be set as the current
      level for the group. If it is omitted, the last set level will be used.

   .. method:: get_dimmers_at(level)

      This method is identical to the previous one, except that the ``level``
      argument to this method should be a raw DMX value (0-255).

.. class:: Group

   Groups provide dictionary-like access to channels, and by default do not
   keep channels set to zero. However, there are two ways to do that:

   .. attribute:: keep_zeros

      Setting this to True will disable the default behavior of dropping
      channels set to 0 from the group.

   .. method:: setzero(channel)

      This method allows a single channel to be set to zero temporarily,
      regardless of the value of the above variable.

.. class:: Cue

   Cues provide dictionary-like access (and read-only attribute access) to
   their meta attributes, including fade times (``up`` and ``down``), wait
   times (``upwait`` and ``downwait``) and follow configuration (``follow``
   and ``followtime``). Channels and groups must be added and set via methods.

   .. method:: persist_defaults

      This method will embed any unchanged default cue attributes within the
      object, ensuring that they remain unchanged if the defaults are changed
      in the system configuration.

   The channel and group methods work the same way, and cues will always
   persist both, even at 0.

   .. method:: add_group(group, intensity)

      This will add or update the group (specified by id, not object) in the
      cue to given level.

   .. method:: remove_group(group)

      This will remove the group specified by the given id from the cue.

   .. method:: add_channel(channel, intensity)

      This will add or update the specified channel in the cue to the given
      level.

   .. method:: remove_group(group)

      This will remove the given channel from the cue.
