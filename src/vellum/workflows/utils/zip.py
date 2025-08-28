import io
import zipfile


def zip_file_map(file_map: dict[str, str]) -> bytes:
    """
    Create a zip file from a dictionary of file names to content.

    Args:
        file_map: Dictionary mapping file names to their content

    Returns:
        Bytes representing the zip file
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in file_map.items():
            zip_file.writestr(filename, content)

    zip_bytes = zip_buffer.getvalue()
    zip_buffer.close()

    return zip_bytes


def extract_zip_files(zip_bytes: bytes) -> dict[str, str]:
    """
    Extract files from a zip archive.

    Args:
        zip_bytes: Bytes representing the zip file

    Returns:
        Dictionary mapping file names to their content
    """
    zip_buffer = io.BytesIO(zip_bytes)
    extracted_files = {}

    with zipfile.ZipFile(zip_buffer) as zip_file:
        for file_name in zip_file.namelist():
            with zip_file.open(file_name) as source:
                content = source.read().decode("utf-8")
                extracted_files[file_name] = content

    return extracted_files
