from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QFileDialog
from PySide6.QtCore import Qt, Signal


class DropZone(QFrame):
    # 既存のシグナル（MainWindow側の変更を不要にするため名前は維持）
    filesDropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # D&Dも一応残しておくことは可能
        self.setMinimumHeight(150)
        # クリック可能であることを示すためにカーソルを指の形にする
        self.setCursor(Qt.PointingHandCursor)

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
        # 文言を「クリックして選択」に変更
        self.label = QLabel("クリックしてファイルを選択")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
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

    # --- クリックイベントの追加 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # ファイル選択ダイアログを表示
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "音楽ファイルを選択",
                "",
                "Audio Files (*.mp3 *.wav *.flac *.m4a);;All Files (*)",
            )
            if files:
                # 取得したリストをシグナルで飛ばす
                self.filesDropped.emit(files)

    # 既存のD&Dイベントは残しておいても実害はありません
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.filesDropped.emit(files)
