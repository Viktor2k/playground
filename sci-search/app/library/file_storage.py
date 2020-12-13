import os


class FileStorageInterface:

    def write(self, input_stream: bytearray, storage_id: str):
        raise NotImplementedError

    def read(self, storage_id):
        raise NotImplementedError

    def delete(self, storage_id):
        raise NotImplementedError


class LocalFileStorage(FileStorageInterface):

    STORAGE_FOLDER = "/Users/Viktor/git/playground/sci-search/file-storage/"

    def __init__(self):
        if not os.path.exists(self.STORAGE_FOLDER):
            os.mkdir(self.STORAGE_FOLDER)

    def write(self, input_stream: bytes, storage_id: str) -> str:
        out_path = self._get_path(storage_id)

        with open(out_path, 'wb+') as out:
            out.write(input_stream)

        return out_path

    def read(self, storage_id) -> bytes:
        path = self._get_path(storage_id)
        with open(path, 'rb') as f:
            return f.read()

    def delete(self, storage_id):
        pass

    def _get_path(self, storage_id: str) -> str:
        return self.STORAGE_FOLDER + storage_id


