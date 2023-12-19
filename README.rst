\$ click\_
==========

.. CXREF:
   https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/adding-a-workflow-status-badge

.. image:: https://github.com/doblabs/click-hotoffthehamster/actions/workflows/checks-unspecial.yml/badge.svg?branch=release
  :target: https://github.com/doblabs/click-hotoffthehamster/actions/workflows/checks-unspecial.yml/badge.svg?branch=release
  :alt: Build Status

.. CXREF: https://app.codecov.io/github.com/doblabs/click-hotoffthehamster/settings/badge

.. image:: https://codecov.io/gh/doblabs/click-hotoffthehamster/branch/release/graph/badge.svg?token=by86aPAzDz
  :target: https://app.codecov.io/gh/doblabs/click-hotoffthehamster
  :alt: Coverage Status

.. image:: https://readthedocs.org/projects/click-hotoffthehamster/badge/?version=latest
  :target: https://click-hotoffthehamster.readthedocs.io/en/latest/
  :alt: Documentation Status

.. image:: https://img.shields.io/github/v/release/doblabs/click-hotoffthehamster.svg?style=flat
  :target: https://github.com/doblabs/click-hotoffthehamster/releases
  :alt: GitHub Release Status

.. image:: https://img.shields.io/pypi/v/click-hotoffthehamster.svg
  :target: https://pypi.org/project/click-hotoffthehamster/
  :alt: PyPI Release Status

.. image:: https://img.shields.io/pypi/pyversions/click-hotoffthehamster.svg
  :target: https://pypi.org/project/click-hotoffthehamster/
  :alt: PyPI Supported Python Versions

.. image:: https://img.shields.io/github/license/doblabs/click-hotoffthehamster.svg?style=flat
  :target: https://github.com/doblabs/click-hotoffthehamster/blob/release/LICENSE
  :alt: License Status

|

Click is a Python package for creating beautiful command line interfaces
in a composable way with as little code as necessary. It's the "Command
Line Interface Creation Kit". It's highly configurable but comes with
sensible defaults out of the box.

It aims to make the process of writing command line tools quick and fun
while also preventing any frustration caused by the inability to
implement an intended CLI API.

Click in three points:

-   Arbitrary nesting of commands
-   Automatic help page generation
-   Supports lazy loading of subcommands at runtime


Installing
----------

Install and update using `pip`_:

.. code-block:: text

    $ pip install -U click

.. _pip: https://pip.pypa.io/en/stable/getting-started/


A Simple Example
----------------

.. code-block:: python

    import click

    @click.command()
    @click.option("--count", default=1, help="Number of greetings.")
    @click.option("--name", prompt="Your name", help="The person to greet.")
    def hello(count, name):
        """Simple program that greets NAME for a total of COUNT times."""
        for _ in range(count):
            click.echo(f"Hello, {name}!")

    if __name__ == '__main__':
        hello()

.. code-block:: text

    $ python hello.py --count=3
    Your name: Click
    Hello, Click!
    Hello, Click!
    Hello, Click!


Donate
------

The Pallets organization develops and supports Click and other popular
packages. In order to grow the community of contributors and users, and
allow the maintainers to devote more time to the projects, `please
donate today`_.

.. _please donate today: https://palletsprojects.com/donate


Links
-----

-   Documentation: https://click.palletsprojects.com/
-   Changes: https://click.palletsprojects.com/changes/
-   PyPI Releases: https://pypi.org/project/click/
-   Source Code: https://github.com/pallets/click
-   Issue Tracker: https://github.com/pallets/click/issues
-   Chat: https://discord.gg/pallets
