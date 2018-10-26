#!/usr/bin/env python
# postfixbuddy.py created by Daniel Hand (daniel.hand@rackspace.co.uk)
# This is a recreation of pfHandle.perl but in Python.

from __future__ import absolute_import, division, print_function
import os
import argparse
from subprocess import call
import subprocess

__version__ = '0.1.0'

# Variables
get_queue_dir = subprocess.Popen(["/usr/sbin/postconf", "-h", "queue_directory"],
                                 stdout=subprocess.PIPE, shell=False)
pf_dir = get_queue_dir.communicate()[0].strip()
active_queue = pf_dir + '/active'
bounce_queue = pf_dir + '/bounce'
corrupt_queue = pf_dir + '/corrupt'
deferred_queue = pf_dir + '/deferred'
hold_queue = pf_dir + '/hold'
incoming_queue = pf_dir + '/incoming'


def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", dest="list_queues",
                        action="store_true",
                        help="List all the current mail queues")
    parser.add_argument('-p', '--purge', dest='purge_queues', type=str,
                        choices=['active', 'bounce', 'corrupt',
                                 'deferred', 'hold', 'incoming'],
                        help="Purge messages from specific queues.")
    parser.add_argument('-m', '--message', dest='delete_mail', type=str,
                        help="Delete specific email based on mailq ID.")
    parser.add_argument('-c', '--clean', dest='clean_queues',
                        action="store_true",
                        help="Purge messages from all queues.")
    parser.add_argument("-H", "--hold", dest="hold_queues",
                        action="store_true",
                        help="Hold all mail queues.")
    parser.add_argument("-r", "--release", dest="release_queues",
                        action="store_true",
                        help="Release all mail queues from held state.")
    parser.add_argument("-f", "--flush", dest="process_queues",
                        action="store_true", help="Flush mail queues")
    parser.add_argument("-D", "--delete", dest="delete_by_address", type=str,
                        help="Delete based on email address")
    parser.add_argument("-S", "--subject", dest="delete_by_subject", type=str,
                        help="Delete based on mail subject")
    parser.add_argument("-s", "--show", dest="show_message", type=str,
                        help="Show message from queue ID")
    version = '%(prog)s ' + __version__
    parser.add_argument('-v', '--version', action='version', version=version)
    return parser


def list_queues():
    queue_list = ['Active', 'Bounce', 'Corrupt',
                  'Deferred', 'Hold', 'Incoming']
    queue_types = [active_queue, bounce_queue, corrupt_queue,
                   deferred_queue, hold_queue, incoming_queue]
    print('============== Mail Queue Summary ==============')
    for index in range(len(queue_list)):
        file_count = sum(len(files) for _, _, files in os.walk(queue_types[index]))
        print(queue_list[index], 'Queue Count:', file_count)
    print


def purge_queues():
    parser = get_options()
    args = parser.parse_args()
    check = str(raw_input(
        "Do you really want to purge the " + args.purge_queues +
        " queue? (Y/N): ")).lower().strip()
    try:
        if check[0] == 'y':
            call(["postsuper", "-d", "ALL", args.purge_queues])
            print("Purged all mail from the " + args.purge_queues + " queue!")
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input')
            return purge_queues()
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return purge_queues()


def clean_queues():
    parser = get_options()
    args = parser.parse_args()
    check = str(raw_input(
        "Do you really want to purge ALL mail queues? (Y/N): "
    )).lower().strip()
    try:
        if check[0] == 'y':
            call(["postsuper", "-d", "ALL"])
            print("Purged all mail queues!")
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input')
            return clean_queues()
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return clean_queues()


def delete_mail():
    parser = get_options()
    args = parser.parse_args()
    check = str(raw_input(
        "Do you really want to delete mail " + args.delete_mail + "? (Y/N): "
    )).lower().strip()
    try:
        if check[0] == 'y':
            call(["postsuper", "-d", args.delete_mail])
            print("Deleted mail ID " + args.delete_mail + "!")
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input')
            return delete_mail()
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return delete_mail()


def hold_queues():
    call(["postsuper", "-h", "ALL"])
    print('All mail queues now on hold!')


def release_queues():
    call(["postsuper", "-H", "ALL"])
    print('Queues no longer in a held state!')


def process_queues():
    call(["postqueue", "-f"])
    print('Flushed all queues!')


def show_message():
    parser = get_options()
    args = parser.parse_args()
    call(["postcat", "-q", args.show_message])


def delete_by_address():
    parser = get_options()
    args = parser.parse_args()
    os.popen('postqueue -p | tail -n +2 | awk \'BEGIN { RS = "" } /' + args.delete_by_address + '/ { print $1 }\' | tr -d \'*!\' | postsuper -d -').read()


def delete_by_subject():
    parser = get_options()
    args = parser.parse_args()
    queue_list = ['Active', 'Bounce', 'Corrupt',
                  'Deferred', 'Hold', 'Incoming']
    queue_types = [active_queue, bounce_queue, corrupt_queue,
                   deferred_queue, hold_queue, incoming_queue]
    for index in range(len(queue_list)):
        print('Searching for mail with this subject in: ' + queue_types[index] + '...')
        os.popen('grep -ri ' + args.delete_by_subject + ' ' + queue_types[index] + ' | awk \'{print $3}\' | cut -d/ -f7 | postsuper -d -').read()


def main():
    parser = get_options()
    args = parser.parse_args()
    if args.list_queues:
        list_queues()
    if args.purge_queues:
        purge_queues()
    if args.clean_queues:
        clean_queues()
    if args.delete_mail:
        delete_mail()
    if args.hold_queues:
        hold_queues()
    if args.release_queues:
        release_queues()
    if args.process_queues:
        process_queues()
    if args.show_message:
        show_message()
    if args.delete_by_address:
        delete_by_address()
    if args.delete_by_subject:
        delete_by_subject()

if __name__ == '__main__':
    main()
