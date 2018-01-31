from urllib import request
import os


DOWNLOAD_ROOT = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    ), 'sources'
)


class Downloader(object):
    TYPE = {
        'jpg': 'images',
        'gif': 'images',
        'png': 'images',
    }

    def __int__(self):
        raise Exception('Downloader类不可被实例化')

    @staticmethod
    def get(uri):
        """ uri(str) -> data(bytes) """
        data = None
        with request.urlopen(uri) as f:
            data = f.read()
        return data

    @classmethod
    def get_by_postfix(cls, uri: str):
        """ uri(str) -> filename(str) """
        postfix = uri.rsplit('.')[-1]
        if postfix in cls.TYPE:
            print(cls.TYPE[postfix])
            _filename = uri.rsplit('/', 1)[-1]
            filename = os.path.join(DOWNLOAD_ROOT, cls.TYPE[postfix], _filename)
            with open(filename, 'wb') as f:
                f.write(Downloader.get(uri))
            return filename


if __name__ == '__main__':
    Downloader.get_by_postfix('http://i7.pdim.gs/addc9b70cbe21f65f031d1a72d84a323.png')
    print(DOWNLOAD_ROOT)