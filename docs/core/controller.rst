Lighting Server
**************************

Central Controller
==========================

.. module:: plc.core.controller
   :synopsis: The core of a :term:`PLC` server, the controller integrates
	      DMX input and output with networked clients and timed events.

.. class:: Controller(settings = conf)
	   
   The :class:`Controller` is the core of a :term:`PLC` server, and integrates
   DMX to and from OLA with messages to and from networked clients, along with
   timed functionality such as Cue faders. It also uses
   :class:`.PersistentData` and automatically saves the cues and groups of
   the show every time they are modified.

   The Controller is a :ref:`Receiver` and implement all of the necessary
   methods to be such.

DMX Hardware Integration
===========================

.. module:: plc.core.integration
   :synopsis: DMX hardware integration via :term:`OLA`

:term:`PLC` provides DMX output via :term:`OLA`.

.. data:: INTEGRATION_MODES

   Dictionary of ``LTP`` or ``HTP`` mode constants. ``HTP`` is not actually
   supported yet, and will just silently revert to ``LTP``.

.. class:: Universe(output, dimmers = DMX_UNIVERSE_SIZE, interval = 100, \
	            mode = INTEGRATION_MODES["LTP"], input = None, \
		    controller = None, allow_ignore_dmx = False)

   This class handles integration with :term:`OLA` for output and possibly
   DMX input. When it receives DMX from :term:`OLA`, it will copy any values
   that have changed since the last set of received DMX frames to the output
   universe based on the integration mode, and also notify an associated
   controller of the both the changed DMX values and the entire set.

   .. attribute:: ignore_dmx

      Setting this to `True` will prevent the :class:`Universe` from copying
      over received DMX input to its DMX output. However, by default setting
      this to `True` is disabled during object instantiation. Additionally,
      the value of this variable does not prevent an associated controller
      from being notified of changed DMX inputs.

   .. method:: set_dimmers(values)

      This method takes a dictionary of channels and DMX values and uses it
      to update the DMX values outputted by the :class:`Universe`. Any values
      outside the acceptable range will be normalized to fit.

.. data:: ola_thread

   This thread must be started by the application to actually send and receive
   DMX frames with :term:`OLA`. Call its :meth:`start` method to begin.
