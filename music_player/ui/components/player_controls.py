import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

# QIcon と QSize をインポートに追加
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Signal


class PlayerControls(QWidget):
    # シグナル定義（変更なし）
    playClicked = Signal()
    pauseClicked = Signal()
    stopClicked = Signal()
    skipForwardClicked = Signal()
    skipBackwardClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        # ボタン間の間隔を少し狭めて引き締める
        layout.setSpacing(15)

        # --- アイコンボタンの作成ヘルパー関数 ---
        def create_icon_button(icon_name):
            btn = QPushButton()
            # アイコンファイルのパス（実行時のカレントディレクトリ基準）
            icon_path = f"styles/icons/{icon_name}.svg"

            # パスが存在するかチェック（デバッグ用）
            if not os.path.exists(icon_path):
                print(f"Warning: Icon not found at {icon_path}")
                btn.setText("?")  # 見つからない場合は「?」を表示

            # アイコンを設定
            btn.setIcon(QIcon(icon_path))
            # アイコンのサイズを指定（ボタンサイズより少し小さく）
            btn.setIconSize(QSize(24, 24))
            # ボタン自体のサイズを固定
            btn.setFixedSize(40, 40)
            # スタイルシートで見た目を調整（ホバー時に少し明るくなど）
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 20px; /* 円形にする */
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """
            )
            return btn

        # 各ボタンを作成
        self.btn_prev = create_icon_button("prev")
        self.btn_stop = create_icon_button("stop")
        self.btn_play = create_icon_button("play")
        self.btn_pause = create_icon_button("pause")
        self.btn_next = create_icon_button("next")

        # シグナルの接続（変更なし）
        self.btn_play.clicked.connect(self.playClicked.emit)
        self.btn_pause.clicked.connect(self.pauseClicked.emit)
        self.btn_stop.clicked.connect(self.stopClicked.emit)
        self.btn_next.clicked.connect(self.skipForwardClicked.emit)
        self.btn_prev.clicked.connect(self.skipBackwardClicked.emit)

        # レイアウトへの追加
        layout.addStretch()
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_play)
        layout.addWidget(self.btn_pause)
        layout.addWidget(self.btn_next)
        layout.addStretch()
