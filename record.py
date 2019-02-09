#!/usr/bin/python3
import signal
import time
from gi.repository import GLib
from pydbus import SessionBus
import os

screencast_bus = SessionBus().get('org.gnome.Shell.Screencast', '/org/gnome/Shell/Screencast')
file_path = os.getcwd() + "output.webm"
frame_rate = int(30)
show_mouse = True
recorder_pipeline = "vp8enc min_quantizer=10 max_quantizer=50 cq_level=13 cpu-used=5 deadline=1000000 threads=%T ! queue ! webmmux"


def main():
    screencast_bus.Screencast(file_path, {'framerate': GLib.Variant('i', int(frame_rate)),
                                          'draw-cursor': GLib.Variant('b', show_mouse),
                                          'pipeline': GLib.Variant('s', recorder_pipeline)})

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to stop video recording.')
    signal.pause()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C, stopping video recording.')
    screencast_bus.StopScreencast()


main()
