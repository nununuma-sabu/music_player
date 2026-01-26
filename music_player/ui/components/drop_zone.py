from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal


class DropZone(QFrame):
    # ファイルがドロップされた時にパスのリストを飛ばすシグナル
    filesDropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # D&Dを許可
        self.setMinimumHeight(150)

        # 見た目の設定（点線の枠など）
        self.setStyleSheet(
            """
            QFrame {
                border: 2px dashed #555;
                border-radius: 10px;
                background-color: #252525;
            }
            QFrame:hover {
                border-color: #00d1b2;
                background-color: #2a2a2a;
            }
        """
        )

        layout = QVBoxLayout(self)
        self.label = QLabel("ここに音楽ファイルをドラッグ＆ドロップ")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            """
    color: #888; 
    border: none; 
    background: none; 
    font-family: 'Meiryo', 'Yu Gothic', 'Microsoft YaHei', sans-serif;
    font-size: 14px;
"""
        )
        layout.addWidget(self.label)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # ドロップされたURLからローカルのファイルパスを抽出
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.filesDropped.emit(files)
