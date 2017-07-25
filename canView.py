#!/usr/bin/env python
"""
logger.py displays CAN traffic.

    python canView.py -c vcan0 -i socketcan

Deps:
python-can - http://python-can.readthedocs.io/en/latest/installation.html
PyGObject - http://pygobject.readthedocs.io/en/latest/getting_started.html
"""
from __future__ import print_function
#import datetime
import argparse
import socket

import can
#from can.io.logger import Logger
from can.listener import Listener
from can.io.sqlite import SqliteWriter

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from canMonitor import LastMessagesWindow
#from thread import start_new_thread, allocate_lock


def open_can_bus():
    parser = argparse.ArgumentParser(description="View CAN traffic")

    parser.add_argument('-c', '--channel', help='''Most backend interfaces require some sort of channel.
    For example with the serial interface the channel might be a rfcomm device: "/dev/rfcomm0"
    With the socketcan interfaces valid channel examples include: "can0", "vcan0"''')

    parser.add_argument('-i', '--interface', dest="interface",
                        help='''Specify the backend CAN interface to use. If left blank,
                        fall back to reading from configuration files.''',
                        choices=can.VALID_INTERFACES)

    parser.add_argument('--filter', help='''One or more filters can be specified for the given CAN interface:
        <can_id>:<can_mask> (matches when <received_can_id> & mask == can_id & mask)
        <can_id>~<can_mask> (matches when <received_can_id> & mask != can_id & mask)
    ''', nargs=argparse.REMAINDER, default='')

    parser.add_argument('-b', '--bitrate', type=int,
                        help='''Bitrate to use for the CAN bus.''')

    results = parser.parse_args()

    can_filters = []
    if len(results.filter) > 0:
        print('Adding filter/s', results.filter)
        for filt in results.filter:
            if ':' in filt:
                _ = filt.split(":")
                can_id, can_mask = int(_[0], base=16), int(_[1], base=16)
            elif "~" in filt:
                can_id, can_mask = filt.split("~")
                can_id = int(can_id, base=16) | 0x20000000    # CAN_INV_FILTER
                can_mask = int(can_mask, base=16) & socket.CAN_ERR_FLAG
            can_filters.append({"can_id": can_id, "can_mask": can_mask})

    config = {"can_filters": can_filters, "single_handle": True}
    if results.interface:
        config["bustype"] = results.interface
    if results.bitrate:
        config["bitrate"] = results.bitrate
    return can.interface.Bus(results.channel, **config)


def on_disp_filter_button_clicked(widget):
    #we set the current language filter to the button's label
    win.current_filter_bits = 0x123
    win.current_filter_mask = 0xfff
    print("%02x&%02x selected!" % (win.current_filter_bits, win.current_filter_mask))
    #we update the filter, which updates in turn the view
    win.canid_filter.refilter()

def on_start_button_clicked(widget):
    #TODO start/stop bus
    pass

def open_history(can_id):
    #TODO open wnd
    if can_id is not None:
        print(hex(can_id)+" History")
    else:
        print("Message History")


class MsgInserter(Listener):
    def __init__(self, MainWnd):
        self.wnd = MainWnd
    def on_message_received(self, msg):
        self.wnd.add_frame(msg)

def main():
    bus = open_can_bus()

    win = LastMessagesWindow(on_start_button_clicked, on_disp_filter_button_clicked, open_history)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()

    db = SqliteWriter("can.db")
    gui = MsgInserter(win)

    can.Notifier(bus, [db, gui])
    
    Gtk.main()
    
    db.stop()
    bus.shutdown()

if __name__ == "__main__":
    main()