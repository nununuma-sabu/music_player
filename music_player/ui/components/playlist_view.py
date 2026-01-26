from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt


class PlaylistView(QListWidget):
    """
    プレイリストを表示するウィジェット
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setStyleSheet(
            """
            QListWidget {
                background-color: #252525;
                border: 1px solid #444;
                border-radius: 5px;
                color: #e0e0e0;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:hover {
                background-color: #2a2a2a;
            }
            QListWidget::item:selected {
                background-color: #333;
                color: #00d1b2;
                border-left: 3px solid #00d1b2;
            }
        """
        )

    def add_song_item(self, metadata):
        """メタデータを受け取り、リストに行を追加する"""
        # 表示形式: "曲名 - アーティスト"
        display_text = f"{metadata['title']}  /  {metadata['artist']}"
        item = QListWidgetItem(display_text)

        # ユーザーには見えないが、内部データとしてファイルパスを保持させておく
        item.setData(Qt.UserRole, metadata["file_path"])

        self.addItem(item)
