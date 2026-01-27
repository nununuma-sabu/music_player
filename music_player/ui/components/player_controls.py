import os
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QSlider,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Signal, Qt
from PySide6.QtMultimedia import QMediaPlayer  # 状態判定用にインポート追加


class PlayerControls(QWidget):
    # シグナル定義
    playPauseClicked = Signal()
    stopClicked = Signal()
    skipForwardClicked = Signal()
    skipBackwardClicked = Signal()
    seekRequested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. 全体を縦に並べるメインレイアウト
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 5, 10, 5)
        self.main_layout.setSpacing(5)

        # 2. 曲情報表示ラベル
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

        # --- 追加: シークバーエリア ---
        self.seek_layout = QHBoxLayout()

        self.label_current = QLabel("00:00")
        self.label_current.setStyleSheet("color: #888; font-size: 11px;")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 4px;
                background: #2a2a2a;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #00d1b2;
                border: 1px solid #00d1b2;
                width: 12px;
                height: 12px;
                margin: -5px 0;
                border-radius: 6px;
            }
        """
        )

        self.label_total = QLabel("00:00")
        self.label_total.setStyleSheet("color: #888; font-size: 11px;")

        self.seek_layout.addWidget(self.label_current)
        self.seek_layout.addWidget(self.slider)
        self.seek_layout.addWidget(self.label_total)
        self.main_layout.addLayout(self.seek_layout)

        # ユーザーがスライダーを動かした時にシグナルを発火
        self.slider.sliderMoved.connect(self.seekRequested.emit)

        # 3. ボタン用の横レイアウト
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(15)

        def create_icon_button(icon_name):
            btn = QPushButton()
            icon_path = f"styles/icons/{icon_name}.svg"
            if not os.path.exists(icon_path):
                btn.setText("?")
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(
                """
                QPushButton { background-color: transparent; border: none; border-radius: 20px; }
                QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }
                QPushButton:pressed { background-color: rgba(255, 255, 255, 0.2); }
            """
            )
            return btn

        # 各ボタンを作成 (btn_playとbtn_pauseを削除し、btn_toggleを作成)
        self.btn_prev = create_icon_button("prev")
        self.btn_stop = create_icon_button("stop")
        self.btn_toggle = create_icon_button("play")  # 初期はplayアイコン
        self.btn_next = create_icon_button("next")

        self.btn_toggle.clicked.connect(self.playPauseClicked.emit)
        self.btn_stop.clicked.connect(self.stopClicked.emit)
        self.btn_next.clicked.connect(self.skipForwardClicked.emit)
        self.btn_prev.clicked.connect(self.skipBackwardClicked.emit)

        # レイアウトへの組み立て（btn_toggleを中央に配置）
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.btn_prev)
        self.button_layout.addWidget(self.btn_stop)
        self.button_layout.addWidget(self.btn_toggle)  # ここを統合
        self.button_layout.addWidget(self.btn_next)
        self.button_layout.addStretch()

        self.main_layout.addLayout(self.button_layout)

    # --- 追加: 表示更新用メソッド ---
    def update_position(self, position_ms, duration_ms):
        """再生位置と時間の表示を更新"""
        if not self.slider.isSliderDown():  # ユーザーがドラッグ中以外のみ自動更新
            self.slider.setValue(position_ms)
        self.label_current.setText(self._format_time(position_ms))
        self.label_total.setText(self._format_time(duration_ms))

    def set_duration(self, duration_ms):
        """曲の長さをスライダーにセット"""
        self.slider.setRange(0, duration_ms)

    def _format_time(self, ms):
        """ミリ秒を MM:SS 形式に変換"""
        s = ms // 1000
        m, s = divmod(s, 60)
        return f"{m:02d}:{s:02d}"

    def update_song_info(self, title, artist):
        self.info_label.setText(f"♪ {title} - {artist}")

    def update_playback_icons(self, state):
        """再生状態に応じてアイコンを切り替える"""
        icon_name = "pause" if state == QMediaPlayer.PlayingState else "play"
        icon_path = f"styles/icons/{icon_name}.svg"

        if os.path.exists(icon_path):
            self.btn_toggle.setIcon(QIcon(icon_path))
        else:
            self.btn_toggle.setText("||" if icon_name == "pause" else ">")
