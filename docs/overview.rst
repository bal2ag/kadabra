.. _overview:

Overview
========

At a high level Kadabra consists of three components:

- A client for collecting the metrics in your application. You will configure
  the client API and instrument your application code to record relevant
  metrics, such as user signups or 500 errors.
- Channels for temporarily queueing the metrics to be published asynchronously.
  Currently the only supported channel is Redis, so all you'll need to do is
  make sure you have a local Redis server running side-by-side with your
  application (this is covered later, don't fret!).
- An agent for dequeueing metrics and publishing them. You will provide
  configuration and run the agent in a dedicated process, separate from your
  application.

Metrics are published asynchronously to have minimal impact on your
application's performance. The client provides a simple interface for gathering
metrics in your application, and the agent takes metrics from the intermediate
channel and publishes them.

If you're ready to start using Kadabra, head on over to :doc:`installation`.
