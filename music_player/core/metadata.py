import os
from mutagen import File as MutagenFile


def extract_metadata(file_path):
    """
    指定された音声ファイルからメタデータを抽出する。
    """
    try:
        audio = MutagenFile(file_path)
        if audio is None:
            return None

        # デフォルト値（ファイル名）
        info = {
            "file_path": file_path,
            "title": os.path.basename(file_path),
            "artist": "Unknown Artist",
            "album": "Unknown Album",
            "composer": "Unknown Composer",
            "duration": int(audio.info.length),
            "album_art": None,
        }

        # タグ情報の解析
        if hasattr(audio, "tags") and audio.tags is not None:
            tags = audio.tags

            # MP3 (ID3) の場合
            if file_path.lower().endswith(".mp3"):
                info["title"] = tags.get("TIT2", [info["title"]])[0]
                info["artist"] = tags.get("TPE1", [info["artist"]])[0]
                info["album"] = tags.get("TALB", [info["album"]])[0]
                # APICタグ (Attached Picture) から取得
                art = tags.getall("APIC")
                if art:
                    info["album_art"] = art[0].data

            # FLAC の場合
            elif file_path.lower().endswith(".flac"):
                info["title"] = tags.get("title", [info["title"]])[0]
                info["artist"] = tags.get("artist", [info["artist"]])[0]
                info["album"] = tags.get("album", [info["album"]])[0]
                # pictures属性から取得
                if getattr(audio, "pictures", None):
                    info["album_art"] = audio.pictures[0].data

            # その他 (Vorbis等)
            else:
                info["title"] = tags.get("title", [info["title"]])[0]
                info["artist"] = tags.get("artist", [info["artist"]])[0]

        return info

    except Exception as e:
        print(f"Metadata extraction error ({os.path.basename(file_path)}): {e}")
        return None
