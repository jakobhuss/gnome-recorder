#!/usr/bin/python3
import argparse
import os
import signal

from gi.repository import GLib
from pydbus import SessionBus

screencast_bus = SessionBus().get('org.gnome.Shell.Screencast', '/org/gnome/Shell/Screencast')
video_pipeline = 'vp8enc min_quantizer=10 max_quantizer=50 cq_level=13 cpu-used=5 deadline=1000000 threads=%T ! queue ! '
audio_on_pipeline = 'mux. pulsesrc ! queue ! audioconvert ! vorbisenc ! queue ! mux. webmmux name=mux'
audio_off_pipeline = 'webmmux'


def build_gstreamer_pipeline(audio=False):
    return video_pipeline + (audio_on_pipeline if audio else audio_off_pipeline)


def main(args):
    screencast_bus.Screencast(args.file_path, {'framerate': GLib.Variant('i', int(args.frame_rate)),
                                               'draw-cursor': GLib.Variant('b', not args.no_cursor),
                                               'pipeline': GLib.Variant('s', build_gstreamer_pipeline(args.audio))})

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to stop video recording.')
    signal.pause()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C, stopping video recording.')
    screencast_bus.StopScreencast()


def parse_arguments():
    args_parser = argparse.ArgumentParser(
        description='Records screen in Gnome using the built in screen recorder functionality',
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    args_parser.add_argument('-o', '--output', default=os.getcwd() + '/output.webm', dest='file_path',
                             help='Output file destination')
    args_parser.add_argument('-n', '--no_cursor', default=False, dest='no_cursor', action='store_true',
                             help='Hide mouse cursor')
    args_parser.add_argument('-a', '--audio_on', default=False, dest='audio', action='store_true',
                             help='Records audio from default pulse audio input')
    args_parser.add_argument('-r', '--frame_rate', type=int, default=30, dest='frame_rate', help='Recording frame rate')
    return args_parser.parse_args()


main(parse_arguments())
