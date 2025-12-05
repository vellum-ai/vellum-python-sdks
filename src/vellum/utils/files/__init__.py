from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "FileNotFoundError": (".exceptions", "FileNotFoundError"),
    "FileRetrievalError": (".exceptions", "FileRetrievalError"),
    "InvalidFileSourceError": (".exceptions", "InvalidFileSourceError"),
    "VellumFileError": (".exceptions", "VellumFileError"),
    "VellumFileMixin": (".mixin", "VellumFileMixin"),
    "read_vellum_file": (".read", "read_vellum_file"),
    "stream_vellum_file": (".stream", "stream_vellum_file"),
    "VellumFileTypes": (".types", "VellumFileTypes"),
    "upload_vellum_file": (".upload", "upload_vellum_file"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    "read_vellum_file",
    "stream_vellum_file",
    "upload_vellum_file",
    "VellumFileTypes",
    "VellumFileMixin",
    "VellumFileError",
    "InvalidFileSourceError",
    "FileRetrievalError",
    "FileNotFoundError",
]
