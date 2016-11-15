.. _api:

API
===

.. module:: kadabra

This covers all the documentation for Kadabra's various classes, including
the Client, Agent, Metrics, Channels, and Publishers.

.. _api-client:

Client
------

.. autoclass:: kadabra.Client
   :members:
   :inherited-members:

.. autoclass:: kadabra.client.Collector
   :members:
   :inherited-members:

.. autoclass:: kadabra.client.CollectorClosedError

.. _api-agent:

Agent
-----

.. autoclass:: kadabra.Agent
   :members:
   :inherited-members:

.. autoclass:: kadabra.agent.Receiver
   :members:
   :inherited-members:

.. autoclass:: kadabra.agent.ReceiverThread
   :members:

.. autoclass:: kadabra.agent.Nanny
   :members:
   :inherited-members:

.. autoclass:: kadabra.agent.NannyThread
   :members:

.. _api-metrics:

Metrics
-------

.. autoclass:: kadabra.Dimension
   :members:
   :inherited-members:

.. autoclass:: kadabra.Counter
   :members:
   :inherited-members:

.. autoclass:: kadabra.Timer
   :members:
   :inherited-members:

.. autoclass:: kadabra.Unit
   :members:
   :inherited-members:

.. autoclass:: kadabra.Units
   :members:
   :inherited-members:

.. autoclass:: kadabra.Metrics
   :members:
   :inherited-members:

.. _api-channels:

Channels
--------

.. autoclass:: kadabra.channels.RedisChannel
   :members:
   :inherited-members:

.. _api-publishers:

Publishers
----------

.. autoclass:: kadabra.publishers.DebugPublisher
   :members:
   :inherited-members:

.. autoclass:: kadabra.publishers.InfluxDBPublisher
   :members:
   :inherited-members:
