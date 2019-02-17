#!/usr/bin/python3
import argparse
import os
import re
import signal
import subprocess

from gi.repository import GLib
from pydbus import SessionBus

screencast_bus = SessionBus().get('org.gnome.Shell.Screencast', '/org/gnome/Shell/Screencast')


def main(args):
    check_print_devices(args)
    check_overwrite_file(args)

    start_recording(args)


def check_overwrite_file(args):
    if os.path.isfile(args.file_path):
        overwrite = input('File already exists. Overwrite? Y = yes, N = no\n')
        if overwrite.lower() in ['n', 'no']:
            exit()


def start_recording(args):
    pipeline = build_gstreamer_pipeline(device=args.audio_device, audio=args.audio)

    screencast_params = {'framerate': GLib.Variant('i', int(args.frame_rate)),
                         'draw-cursor': GLib.Variant('b', not args.no_cursor),
                         'pipeline': GLib.Variant('s', pipeline)}

    screencast_bus.Screencast(args.file_path, screencast_params)
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to stop video recording.')
    signal.pause()


def check_print_devices(args):
    if args.list_devices:
        for i, device in enumerate(audio_devices()):
            print()
            print('number: {}'.format(i))
            print('name: {}'.format(device))
        exit()


def signal_handler(sig, frame):
    print('You pressed Ctrl+C, stopping video recording.')
    screencast_bus.StopScreencast()


def build_gstreamer_pipeline(device=None, audio=False):
    video_pipeline = 'vp8enc min_quantizer=10 max_quantizer=50 cq_level=13 cpu-used=5 deadline=1000000 threads=%T ! queue ! '
    audio_device_pipeline = 'mux. pulsesrc device={} ! queue ! audioconvert ! vorbisenc ! queue ! mux. webmmux name=mux'
    audio_on_pipeline = 'mux. pulsesrc ! queue ! audioconvert ! vorbisenc ! queue ! mux. webmmux name=mux'
    audio_off_pipeline = 'webmmux'

    pipeline = video_pipeline

    if device:
        if device.isdigit():
            device = audio_devices()[int(device)]
        return pipeline + audio_device_pipeline.format(device)

    if audio:
        return pipeline + audio_on_pipeline

    return pipeline + audio_off_pipeline


def audio_devices():
    pacmd_sources = subprocess.run(['pacmd', 'list-sources'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    return re.findall('name: <(.*)>', pacmd_sources)


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
    args_parser.add_argument('-l', '--list_devices', default=False, dest='list_devices', action='store_true',
                             help='List possible audio devices for pulse audio')
    args_parser.add_argument('-d', '--audio_device', dest='audio_device',
                             help='Pulse audio device name or number for audio recording')
    args_parser.add_argument('-r', '--frame_rate', type=int, default=30, dest='frame_rate', help='Recording frame rate')
    return args_parser.parse_args()


if __name__ == '__main__':
    main(parse_arguments())
