CANView
==========

This is a cross platform GTK3 Programm to display and send
**C**\ ontroller **A**\ rea **N**\ etwork messages.

For now, it displays the last messages and logs all CAN frames to a SQLite DB.

Installation
----------

Install `python-can <http://python-can.readthedocs.io/en/latest/installation.html>`__.
Install `PyGObject <http://pygobject.readthedocs.io/en/latest/getting_started.html>`__.
Clone this Repo.
Run the Program ``python canView.py -c vcan0 -i socketcan``.
