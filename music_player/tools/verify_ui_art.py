import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC


def get_art_binary(file_path):
    """ファイルから画像のバイナリデータだけを抜き出す"""
    try:
        if file_path.endswith(".flac"):
            audio = FLAC(file_path)
            return audio.pictures[0].data if audio.pictures else None
        elif file_path.endswith(".mp3"):
            audio = MP3(file_path, ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    return tag.data
    except Exception as e:
        print(f"Error: {e}")
    return None


def main():
    app = QApplication(sys.argv)

    # 1. 検証したいファイルパスを指定
    target_file = "test.flac"
    binary_data = get_art_binary(target_file)

    if not binary_data:
        print("画像データが見つかりませんでした。")
        return

    # 2. ウィンドウとラベルの準備
    window = QWidget()
    window.setWindowTitle("Album Art Verification")
    layout = QVBoxLayout(window)

    label = QLabel("Loading...")
    label.setFixedSize(300, 300)
    label.setScaledContents(True)  # 画像をラベルサイズに合わせる設定

    # 3. ★ここが本番でも使う「バイナリ -> 画像変換」の肝です
    pixmap = QPixmap()
    success = pixmap.loadFromData(binary_data)

    if success:
        label.setPixmap(pixmap)
        print("✅ 画面への表示に成功しました！")
    else:
        label.setText("画像の読み込みに失敗しました")
        print("❌ バイナリデータが画像として認識されませんでした")

    layout.addWidget(label)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
