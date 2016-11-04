.. _overview:

Overview
========

Kadabra consists of three components:

- A client for collecting the metrics in your application. You will configure
  and use the client API inside your application code. See :doc:`collecting`.
- Channels for temporarily queueing the metrics to be published into storage
  asynchronously. At most you will only need to provide configuration; often
  you won't even need to do that as the defaults will be fine. See 
  :doc:`sending`.
- An agent for dequeueing metrics and publishing them into storage. You will
  provide configuration and run the agent in a dedicated process, separate from
  your application. See :doc:`publishing`. 

Metrics are published asynchronously to have minimal impact on your
application's performance. The client provides a simple interface for gathering
metrics in your application, and the agent takes metrics from the intermediate
channel and publishes them to your metrics database.

For simple setup to get started, see :doc:`gettingstarted`.
