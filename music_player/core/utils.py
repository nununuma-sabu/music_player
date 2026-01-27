import os
import sys


def get_asset_path(relative_path):
    """
    開発環境と PyInstaller (exe化) の両方で、
    正しいリソース（画像など）のパスを取得するための関数です。
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller でビルドされた実行ファイルとして動いている場合
        # 一時展開先のパスを参照します
        return os.path.join(sys._MEIPASS, relative_path)

    # 通常の Python スクリプトとして動いている場合
    # プロジェクトのルートディレクトリを基準にします
    return os.path.join(os.path.abspath("."), relative_path)
