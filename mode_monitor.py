#!/usr/bin/python3

import subprocess
import sys
import argparse
import re
# Usage: python mode_monitor.py <interface> <mode> --random-mac


class Interface:
    def __init__(self, name):
        self.name = name
        self.mode = self.__get_current_mode()

    def __get_current_mode(self):
        cmd = subprocess.run(
            ['sudo', 'iw', 'dev', self.name, 'info'], capture_output=True, text=True)
        return re.search('(?<=type )\w+', cmd.stdout).group()

    def up(self):
        self.__cmd_output = subprocess.run(
            ['sudo', 'ip', 'link', 'set', 'dev', self.name, 'up'], capture_output=True, text=True)

    def down(self):
        self.__cmd_output = subprocess.run(
            ['sudo', 'ip', 'link', 'set', 'dev', self.name, 'down'], capture_output=True, text=True)

    def set_random_mac(self):
        self.down()
        self.__cmd_output = subprocess.run(
            ['sudo', 'macchanger', '-r', self.name], capture_output=True, text=True)
        self.up()

    def set_mode(self, mode):
        if mode not in ['monitor', 'managed']:
            raise ValueError('mode must be "monitor" or "managed"')

        self.down()
        self.__cmd_output = subprocess.run(
            ['sudo', 'iwconfig', self.name, 'mode', mode], capture_output=True, text=True)
        self.up()
        self.mode = self.__get_current_mode()


if __name__ == '__main__':
    args = argparse.ArgumentParser(
        'mode_monitor.py', 'python3 mode_monitor.py <interface> <mode> --random-mac',)
    args.add_argument('interface', type=str)
    args.add_argument('mode', type=str,
                      choices=['monitor', 'managed'])
    args.add_argument('-r', '--random-mac')
    args = args.parse_args()

    wifi = Interface(args.interface)
    if wifi.mode == args.mode:
        print('Interface already in ' + args.mode + ' mode')
        sys.exit()
    wifi.set_mode(args.mode)
    if args.random_mac:
        wifi.set_random_mac()
