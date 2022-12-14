# Date: 05/11/2022
# Author: DREAD.DR
# Description: File manager


class File:

    chunk_size = (64 << 10) - 1

    @classmethod
    def read(cls, file, _bytes=True, chunk_size=None):

        if not chunk_size:
            chunk_size = cls.chunk_size

        with open(file, 'rb' if _bytes else 'rt') as f:
            while True:
                data = f.read(chunk_size)
                if data:
                    yield data
                else:
                    break

    @classmethod
    def write(cls, file, data):
        with open(file, 'wb') as f:
            for n in range(0, len(data), cls.chunk_size):
                _max = n + cls.chunk_size
                _data = data[n:_max]
                f.write(_data.encode() if isinstance(_data, str) else _data)
