import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from ui.main_window import MainWindow


def main():
    # GUIアプリケーションのインスタンス作成
    app = QApplication(sys.argv)

    # --- WSL/Linux環境向けのフォント設定 ---
    # インストールした日本語フォントを優先的に探します
    # Noto Sans CJK JP や IPAGothic が WSLg では一般的です
    font_families = ["Noto Sans CJK JP", "IPAGothic", "TakaoGothic", "DejaVu Sans"]
    selected_font = None

    for family in font_families:
        font = QFont(family, 10)
        # exactMatchは環境により挙動が異なるため、
        # 確実に設定したい場合は一番手近なインストール済みフォントを指定します
        selected_font = font
        break

    if selected_font:
        app.setFont(selected_font)

    # --- QSS（スタイルシート）の読み込み ---
    # music_player/styles/theme.qss を UTF-8 で読み込みます
    base_dir = os.path.dirname(__file__)
    qss_path = os.path.join(base_dir, "styles", "theme.qss")

    if os.path.exists(qss_path):
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"スタイルシートの読み込みエラー: {e}")
    else:
        print(f"警告: スタイルシートが見つかりません: {qss_path}")

    # メインウィンドウの表示
    window = MainWindow()
    window.show()

    # イベントループの開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
