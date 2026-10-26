from uuid import UUID


def process_video_task(file_path: str, camera_id: UUID, storage_key: str):
    print(f"Processing video file: {file_path}, storage_key: {storage_key}")


# import subprocess
#
# def extract_first_frame(video_path: str, out_path: str) -> None:
#     subprocess.run(
#         [
#             "ffmpeg",
#             "-y",                # перезаписать out_path, если есть
#             "-i", video_path,    # входной файл
#             "-frames:v", "1",    # взять один кадр
#             "-q:v", "2",         # качество JPEG (2 — высокое)
#             out_path,
#         ],
#         check=True,              # CalledProcessError при ненулевом коде возврата
#         capture_output=True,     # не засорять вывод, stderr доступен в исключении
#         timeout=30,
#     )
