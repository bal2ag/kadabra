Kadabra - Metrics Made Easy
===========================

.. image:: https://secure.travis-ci.org/bal2ag/kadabra.png?branch=master
    :target: http://travis-ci.org/bal2ag/kadabra
    :alt: Build

.. image:: https://readthedocs.org/projects/kadabra/badge/?version=latest&style
    :target: http://kadabra.readthedocs.org/
    :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/bal2ag/kadabra/badge.svg?branch=master
    :target: https://coveralls.io/github/bal2ag/kadabra?branch=master
    :alt: Coverage

You need to know what's going on with your Python application. How many people
signed up today? How often does it crash? How long did it take to run your
weekly processing jobs? How many orders did you fill yesterday?

You should be able to answer these questions quickly and easily. It shouldn't
be a hassle to check the status of your web app, or answer important business
questions about your service. And it shouldn't cost a fortune. There are plenty
of metrics services out there, but they `cost
<https://newrelic.com/calculator>`_ a `lot
<https://azure.microsoft.com/en-us/pricing/details/application-insights/>`_ of
`money <https://aws.amazon.com/cloudwatch/pricing/>`_ and sometimes even
require some sort of contractual commitment. And they usually give you more
than you really need.

Kadabra provides a simple API to instrument your application code to record
metrics and a performant, reliable agent to publish your metrics into a
database. It is cost-effective, scales with your application, is fully
unit-tested, and best of all, it runs *completely on open-source software.*

If you're willing to put in a bit of work, you can save a lot of money and
maintain control of your application infrastructure.

Installation
------------

Installation is easy with pip::

    pip install Kadabra

Usage
-----

Instrument your code to record metrics with a simple API::

    import kadabra
    client = kadabra.Client()
    metrics = client.get_collector()
    ...
    metrics.add_count("userSignup", 1.0)
    ...
    metrics.add_count("success", 1.0)
    ...
    client.send(metrics.close())

Then configure and run the agent in a separate process to publish your metrics
into a database!

Docs
----

The `documentation <http://kadabra.readthedocs.io/en/latest/overview.html>`_
contains complete instructions to get up and running with Kadabra, including
usage guides and the fully-documented API.
