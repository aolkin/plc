Networking
*************************

Protocol
=========================

.. module:: plc.network.protocols
   :synopsis: The asyncio-compatible Protocol classes

The PLC network protocol works by sending pickled :class:`.Message` objects,
whose :meth:`~.Message.action` methods are called by the receiving code. In
version 1 of the protocol, every message begins with a 3 byte header, the
first byte containing the protocol version number, and the next two the size
of the remaining message.

.. autoclass:: PLCProtocol

   Both the client and server Protocols share these methods:

   .. automethod:: send_message

      This method should be used to send a :class:`.Message` object.

   .. automethod:: on_message

      The default implementation of calling the message's
      :meth:`~.Message.action` method with the Protocol should probably not
      be changed.

   Both the client and server protocols have these methods, but possess
   different implementations.

   .. automethod:: connection_made

   .. method:: connection_lost(exc)

.. autoclass:: ServerProtocol
	      
   The `controller` argument must be an instance of a subclass of
   :class:`.Receiver`.

.. autoclass:: ClientProtocol
	    
   The `client` argument must be an instance of a subclass of
   :class:`.Receiver`.

..
   Authentication
   -------------------------

   .. module:: plc.network.authentication
      :synopsis: Provides helpers for authentication to a server.

   Authentication support currently doesn't work too well, and may be dropped
   soon.

   .. autoclass:: plc.network.authentication.User
       :members:
       :undoc-members:

Receiving Messages
===========================

.. module:: plc.network.receiver
   :synopsis: Provides the interface for Protocol receivers

Both the client and server protocols take a :class:`Receiver` subclass as
an argument to their constructor. Receiver subclasses must implement all
of the methods listed here.

.. autoclass:: Receiver
    :members:

Sending Commands
===========================

.. module:: plc.network.messages
   :synopsis: Provides the various message classes that may be sent

Commands and information are sent via the relevant :class:`.PLCProtocol`
subclass's :meth:`~.PLCProtocol.send_message` method by passing in an
instance of a :class:`Message` subclass.

.. class:: Message

   All messages have the same basic interface and work the same way:
   When instantiated, any positional arguments passed are stored as a list,
   and any keyword arguments are both stored as a dictionary and inserted
   into the object's `__dict__`. This allows that data to be sent when the
   object is pickled for transport.

   :class:`Message` objects also provide list-like access to the stored
   positional arguments, as well as :func:`len` access to the length of
   that list.

   .. automethod:: action

      The action method always takes a single argument, the
      :class:`.PLCProtocol` subclass instance to act upon. The default
      implementation merely calls the method of that protocol instance's
      receiver corresponding to the class name of the Message (e.g.
      :meth:`~.Receiver.dimmer` for a :class:`DimmerMessage`.) with the
      positional and keyword arguments given to the :class:`Message`
      object at instantiation expanded as positional and keyword
      arguments for that method. 

However, while that default implementation is sufficient for some messages,
most have more specific :meth:`~Message.action` methods.

.. class:: DimmerMessage(dimmers, source=None)

   This message is used by the server to send the current levels for
   channels, and by clients to set levels per-channel manually.

   The optional `source` argument is used to indicate where this set of
   channel levels originated, and can be used by clients to style their
   channel display. For example, on DMX input, the server supplies a
   value of ``"input"`` as the `source`.

:class:`GroupMessage` and :class:`CueMessage` work similarly: if updating,
(action is ``"update"``), the second argument should be an object, which will
be added to the receiver's appropriate registry and have its registry
updated to match. It will overwrite any existing object with the same id.
Otherwise, the second argument should be an id, and the requisite object will
then be retrieved from the registry before calling the appropriate method on
the :class:`.Receiver`.

.. class:: CueMessage(action, cue)

.. class:: GroupMessage(action, group, [level])
   
   :class:`GroupMessage` also accepts a third argument, and if the action is
   ``"level"`` or ``"update"``, then the group's level will be set before
   continuing.

These messages should generally not be sent by custom code:

.. autoclass:: ResultMessage

.. class:: AuthMessage(username, hashed password)

   Both arguments must be passed positionally, not by keyword.

   This message's action should only be invoked on the server.

.. class:: RegistryMessage(type, registry)

   This message is sent to clients when they connect to provide them with
   full copies of the cue and group lists. Both arguments are positional.

.. class:: RequestMessage(type, id)

   Arguments must be passed positionally.

   This message should be used by clients to request an updated copy of
   the requested group or cue. The server will respond with the appropriate
   :class:`GroupMessage` or :class:`CueMessage`.
