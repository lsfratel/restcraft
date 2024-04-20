class UploadedFile:
    """
    Represents an uploaded file.

    Attributes:
        filename (str): The name of the uploaded file.
        content_type (str): The content type of the uploaded file.
        filepath (str): The file path of the uploaded file.
    """

    __slots__ = ('filename', 'content_type', 'filepath')

    def __init__(self, filename: str, content_type: str, filepath: str):
        self.filename = filename
        self.content_type = content_type
        self.filepath = filepath

    def __repr__(self) -> str:
        return f'<UploadedFile {self.filename} {self.filepath}>'
