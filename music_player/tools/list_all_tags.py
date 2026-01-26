import sys
import os
from mutagen import File


def list_all_tags(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found -> {file_path}")
        return

    audio = File(file_path)
    if audio is None:
        print("Error: Could not parse file.")
        return

    print(f"\n{'='*20} All Metadata Keys {'='*20}")
    print(f"File: {os.path.basename(file_path)}")
    print(f"Format: {type(audio).__name__}")
    print("-" * 50)

    if audio.tags:
        # すべてのタグ名（キー）を取得してソートして表示
        tag_keys = sorted(audio.tags.keys())
        for key in tag_keys:
            # 値が長すぎる場合（歌詞など）を考慮して、改行は適宜処理
            value = audio.tags.get(key)
            print(f"{key:20} : {value}")
    else:
        print("No tags found in this file.")

    print("=" * 50)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python list_all_tags.py <path_to_audio_file>")
    else:
        list_all_tags(sys.argv[1])
