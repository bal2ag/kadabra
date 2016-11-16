.. _runninginprod:

Running in Production
=====================

Kadabra's client can be very easily integrated into your application's code.
But how do you run the agent alongside your application in a production
environment? How do you ensure that when your application shuts down, the agent
shuts down gracefully without losing metrics?

You will typically want to run a long-running process like the agent under a
process control system such as `supervisord <http://supervisord.org/>`_. Such a
program ensures that the agent is restarted if it is suddenly killed, and will
usually be part of your broader application deployment system for managing
other processes you might want to run on the same host.

Most of these systems will communicate to the processes under their control the
need to shutdown using operating system `signals
<https://en.wikipedia.org/wiki/Unix_signal#POSIX_signals>`_. The process that
runs the Kadabra agent should respond to these signals by calling the agent's
:meth:`~kadabra.Agent.stop` method, which gracefully shuts down the agent and
all associated threads, ensuring that none of them are killed in the process of
publishing metrics.

For example, you could use this simple program to run your agent::

    from kadabra import Agent

    import logging, sys, os, signal

    agent = Agent()
    signal.signal(signal.SIGINT, agent.stop)
    signal.signal(signal.SIGTERM, agent.stop)
    agent.start()

This will ensure that when the process control system sends a ``SIGINT`` or
``SIGTERM`` signal to your agent process, it will shut down gracefully.

.. note:: Although this will prevent the agent from shutting down in the middle
          of publishing metrics, it does not guarantee that the channel queues
          will be completely empty. There may still be pending metrics,
          depending on how often your application publishes metrics and how
          fast the metrics get published. Thus it's also a good idea to backup
          your channel periodically so you can restore pending metrics when
          your application starts up again. For example, if you use the
          :class:`~kadabra.channels.RedisChannel` you can set up Redis
          `snapshots <http://redis.io/topics/persistence>`_.
