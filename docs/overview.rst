.. _overview:

Overview
========

Kadabra consists of three components:

- A client for collecting the metrics in your application. You will configure
  and use the client API inside your application code.
- Channels for temporarily queueing the metrics to be published asynchronously.
  At most you will only need to provide configuration; often you won't even
  need to do that as the defaults will be fine.
- An agent for dequeueing metrics and publishing them. You will provide
  configuration and run the agent in a dedicated process, separate from your
  application.

Metrics are published asynchronously to have minimal impact on your
application's performance. The client provides a simple interface for gathering
metrics in your application, and the agent takes metrics from the intermediate
channel and publishes them.

To get up and running with Kadabra, see :doc:`gettingstarted`.
