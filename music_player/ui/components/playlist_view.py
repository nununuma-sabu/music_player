from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeyEvent, QAction


class PlaylistView(QListWidget):
    """プレイリストを表示するウィジェット"""

    songSelected = Signal(str)
    # 削除操作が行われた際に、そのインデックスを通知するシグナル
    songDeleted = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        # スタイル設定
        self.setStyleSheet(
            """
            QListWidget {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 5px;
                color: #ddd;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #222;
            }
            QListWidget::item:selected {
                background-color: #2c2c2c;
                color: #00f2c3;
                border-left: 3px solid #00f2c3;
            }
            QListWidget::item:hover {
                background-color: #252525;
            }
        """
        )

    def keyPressEvent(self, event: QKeyEvent):
        """Deleteキーによる削除対応"""
        if event.key() == Qt.Key_Delete:
            current_row = self.currentRow()
            if current_row >= 0:
                self.songDeleted.emit(current_row)
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        """右クリックメニューの作成と表示"""
        item = self.itemAt(event.pos())
        if not item:
            return

        menu = QMenu(self)
        # スタイルの適用（ダークテーマに合わせる）
        menu.setStyleSheet(
            """
            QMenu { background-color: #2b2b2b; color: white; border: 1px solid #333; }
            QMenu::item:selected { background-color: #3d3d3d; }
        """
        )

        delete_action = QAction("削除", self)
        delete_action.triggered.connect(lambda: self.songDeleted.emit(self.row(item)))
        menu.addAction(delete_action)

        menu.exec(event.globalPos())

    def _on_item_double_clicked(self, item):
        file_path = item.data(Qt.UserRole)
        self.songSelected.emit(file_path)

    def add_song_item(self, metadata):
        title = metadata.get("title", "Unknown")
        artist = metadata.get("artist", "Unknown")
        item = QListWidgetItem(f"{title} - {artist}")
        item.setData(Qt.UserRole, metadata["file_path"])
        self.addItem(item)
