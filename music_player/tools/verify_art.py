import os
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC


def verify_album_art(file_path):
    print(f"Checking: {file_path}")

    if file_path.endswith(".flac"):
        audio = FLAC(file_path)
        # FLACの画像データは 'pictures' 属性に格納される
        if audio.pictures:
            picture = audio.pictures[0]
            with open("extracted_cover.jpg", "wb") as f:
                f.write(picture.data)
            print("✅ FLAC cover image extracted to 'extracted_cover.jpg'")
        else:
            print("❌ No picture found in FLAC.")

    elif file_path.endswith(".mp3"):
        audio = MP3(file_path, ID3=ID3)
        # MP3(ID3)の場合は APIC フレームを探す
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                with open("extracted_cover.jpg", "wb") as f:
                    f.write(tag.data)
                print("✅ MP3 cover image extracted to 'extracted_cover.jpg'")
                return
        print("❌ No APIC tag found in MP3.")


if __name__ == "__main__":
    # 今テストで使っている実際のファイルを指定してみてください
    target_file = "test.flac"
    if os.path.exists(target_file):
        verify_album_art(target_file)
    else:
        print(f"File not found: {target_file}")
