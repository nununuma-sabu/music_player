import os
import sys
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QSlider,
    QToolTip,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Signal, Qt
from PySide6.QtMultimedia import QMediaPlayer
from .clickable_slider import ClickableSlider


def get_asset_path(relative_path):
    """.exe化しても画像を見つけられるように絶対パスを解決する関数"""
    if hasattr(sys, "_MEIPASS"):
        # PyInstallerの一時展開先を参照
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class PlayerControls(QWidget):
    playPauseClicked = Signal()
    stopClicked = Signal()
    skipForwardClicked = Signal()
    skipBackwardClicked = Signal()
    seekRequested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 5, 10, 5)
        self.main_layout.setSpacing(5)

        # 1. 曲情報表示ラベル
        self.info_label = QLabel("No Song Selected")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(
            """
            color: #00f2c3; 
            font-weight: bold; 
            font-size: 14px;
            background: transparent;
        """
        )
        self.main_layout.addWidget(self.info_label)

        # 2. シークバーエリア
        self.seek_layout = QHBoxLayout()
        self.label_current = QLabel("00:00")
        self.label_current.setStyleSheet("color: #888; font-size: 11px;")

        self.slider = ClickableSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setStyleSheet(
            """
            QSlider::groove:horizontal { border: 1px solid #444; height: 4px; background: #2a2a2a; margin: 2px 0; }
            QSlider::handle:horizontal { background: #00f2c3; border: 1px solid #00f2c3; width: 12px; height: 12px; margin: -5px 0; border-radius: 6px; }
        """
        )

        self.label_total = QLabel("00:00")
        self.label_total.setStyleSheet("color: #888; font-size: 11px;")

        self.seek_layout.addWidget(self.label_current)
        self.seek_layout.addWidget(self.slider)
        self.seek_layout.addWidget(self.label_total)
        self.main_layout.addLayout(self.seek_layout)

        self.slider.sliderMoved.connect(self.seekRequested.emit)

        # 3. ボタンとボリューム用の横レイアウト
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(15)

        # アイコンボタン作成用ヘルパー
        def create_icon_button(icon_name):
            btn = QPushButton()
            icon_path = get_asset_path(f"styles/icons/{icon_name}.svg")

            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
            else:
                btn.setText("?")

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

        # 各ボタン作成
        self.btn_prev = create_icon_button("prev")
        self.btn_stop = create_icon_button("stop")
        self.btn_toggle = create_icon_button("play")
        self.btn_next = create_icon_button("next")

        # ★ 音量調整エリアの作成
        self.vol_label = QLabel("Vol:")
        self.vol_label.setStyleSheet("color: #888; font-size: 11px;")

        # 修正箇所: QSlider から ClickableSlider に変更
        self.volume_slider = ClickableSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)  # 初期値は安全な50%
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setStyleSheet(
            """
            QSlider::groove:horizontal { border: 1px solid #444; height: 4px; background: #2a2a2a; }
            QSlider::handle:horizontal { background: #00f2c3; width: 10px; height: 10px; border-radius: 5px; margin: -3px 0; }
        """
        )

        # --- レイアウト組み立て ---
        self.button_layout.addStretch()

        # 中央：再生コントロール
        self.button_layout.addWidget(self.btn_prev)
        self.button_layout.addWidget(self.btn_stop)
        self.button_layout.addWidget(self.btn_toggle)
        self.button_layout.addWidget(self.btn_next)

        self.button_layout.addStretch()

        # ★ 右端：ボリュームコントロール
        self.button_layout.addWidget(self.vol_label)
        self.button_layout.addWidget(self.volume_slider)

        self.main_layout.addLayout(self.button_layout)

        # 接続設定
        self.btn_toggle.clicked.connect(self.playPauseClicked.emit)
        self.btn_stop.clicked.connect(self.stopClicked.emit)
        self.btn_next.clicked.connect(self.skipForwardClicked.emit)
        self.btn_prev.clicked.connect(self.skipBackwardClicked.emit)

        # 追加: 各スライダーのホバーイベントを接続
        self.slider.hoveredValue.connect(self._show_hover_time)
        self.volume_slider.hoveredValue.connect(self._show_hover_volume)

    def update_position(self, position_ms, duration_ms):
        if not self.slider.isSliderDown():
            self.slider.setValue(position_ms)
        self.label_current.setText(self._format_time(position_ms))
        self.label_total.setText(self._format_time(duration_ms))

    def set_duration(self, duration_ms):
        self.slider.setRange(0, duration_ms)

    def _format_time(self, ms):
        s = ms // 1000
        m, s = divmod(s, 60)
        return f"{m:02d}:{s:02d}"

    def update_song_info(self, title, artist):
        self.info_label.setText(f"♪ {title} - {artist}")

    def update_playback_icons(self, state):
        """再生状態に応じてアイコンを切り替える"""
        icon_name = "pause" if state == QMediaPlayer.PlayingState else "play"
        icon_path = get_asset_path(f"styles/icons/{icon_name}.svg")

        if os.path.exists(icon_path):
            self.btn_toggle.setIcon(QIcon(icon_path))
        else:
            self.btn_toggle.setText("||" if icon_name == "pause" else ">")

    # 追加: シークバーのツールチップ表示
    def _show_hover_time(self, value_ms, global_pos):
        if self.slider.maximum() > 0:
            time_str = self._format_time(value_ms)
            QToolTip.showText(global_pos, time_str, self.slider)

    # 追加: ボリュームのツールチップ表示
    def _show_hover_volume(self, value, global_pos):
        """ホバー位置の音量をツールチップで表示"""
        QToolTip.showText(global_pos, f"Vol: {value}%", self.volume_slider)
