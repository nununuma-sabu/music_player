import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Signal, Qt


class PlayerControls(QWidget):
    # シグナル定義
    playClicked = Signal()
    pauseClicked = Signal()
    stopClicked = Signal()
    skipForwardClicked = Signal()
    skipBackwardClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. 全体を縦に並べるメインレイアウトを新設
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 5, 0, 5)  # 上下の余白を微調整
        self.main_layout.setSpacing(5)

        # 2. 曲情報表示ラベルの追加
        self.info_label = QLabel("No Song Selected")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(
            """
            color: #00d1b2; 
            font-weight: bold; 
            font-size: 14px;
            background: transparent;
        """
        )
        self.main_layout.addWidget(self.info_label)

        # 3. ボタン用の横レイアウト（既存の構成を継承）
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(15)

        # アイコンボタンの作成ヘルパー関数
        def create_icon_button(icon_name):
            btn = QPushButton()
            icon_path = f"styles/icons/{icon_name}.svg"

            if not os.path.exists(icon_path):
                print(f"Warning: Icon not found at {icon_path}")
                btn.setText("?")

            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 20px;
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

        # シグナルの接続
        self.btn_play.clicked.connect(self.playClicked.emit)
        self.btn_pause.clicked.connect(self.pauseClicked.emit)
        self.btn_stop.clicked.connect(self.stopClicked.emit)
        self.btn_next.clicked.connect(self.skipForwardClicked.emit)
        self.btn_prev.clicked.connect(self.skipBackwardClicked.emit)

        # レイアウトへの組み立て
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.btn_prev)
        self.button_layout.addWidget(self.btn_stop)
        self.button_layout.addWidget(self.btn_play)
        self.button_layout.addWidget(self.btn_pause)
        self.button_layout.addWidget(self.btn_next)
        self.button_layout.addStretch()

        # メインレイアウトにボタン列を追加
        self.main_layout.addLayout(self.button_layout)

    def update_song_info(self, title, artist):
        """外部から曲情報を更新するためのメソッド"""
        self.info_label.setText(f"♪ {title} - {artist}")
