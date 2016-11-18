Kadabra - Metrics Made Easy
===========================

You need to know what's going on with your Python application. How many people
signed up today? How often does it crash? How long did it take to run your
weekly processing jobs? How many orders did you fill yesterday?

You should be able to answer these questions quickly and easily. It shouldn't
be a hassle to check the status of your web app, or answer important business
questions about your service. And it shouldn't cost a fortune. There are plenty
of metrics services out there, but they `cost
<https://newrelic.com/calculator>`_ a `lot
<https://azure.microsoft.com/en-us/pricing/details/application-insights/>`_ of
`money <https://aws.amazon.com/cloudwatch/pricing/>`_ and somtimes require some
sort of contractual commitment. And they usually give you more than you really
need.

Kadabra provides a simple API to instrument your application code to record
metrics and a performant, reliable agent to publish your metrics into a
database. It is cost-effective, scales with your application, unit-tested,
and best of all, runs `completely on open-source software.`

If you're willing to put in a bit of work, you can save money and headache and
maintain control of your application infrastructure.

Head on over to the :doc:`overview` section to get started.

Contents:
---------

.. toctree::
   :maxdepth: 2

   overview
   installation
   gettingstarted
   configuration
   collecting
   sending
   publishing
   usingwithinfluxdb
   runninginprod
   api
