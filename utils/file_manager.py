from streamlit.runtime.uploaded_file_manager import UploadedFile

class FileManager:
  """
  管理文件
  """
  @staticmethod
  def save_uploaded_file(file: UploadedFile, save_path: str) -> None:
    """
    保存上传文件
    """
    with open(save_path, "wb") as f:
      f.write(file.getvalue())
