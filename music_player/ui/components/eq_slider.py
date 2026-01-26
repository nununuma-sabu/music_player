from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel
from PySide6.QtCore import Qt, Signal


class EqSlider(QWidget):
    # 値が変わった時に外部（エンジン側など）に通知するための独自シグナル
    valueChanged = Signal(str, int)

    def __init__(self, frequency, parent=None):
        super().__init__(parent)
        self.frequency = frequency

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 10, 5, 10)

        # 現在のゲイン表示 (例: +3dB)
        self.value_label = QLabel("0dB")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet(
            "color: #00d1b2; font-weight: bold; font-family: 'Consolas';"
        )

        # スライダー本体
        self.slider = QSlider(Qt.Vertical)
        self.slider.setRange(-12, 12)  # ±12dB
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(3)

        # 周波数ラベル (例: 1kHz)
        self.freq_label = QLabel(self.frequency)
        self.freq_label.setAlignment(Qt.AlignCenter)
        self.freq_label.setStyleSheet("color: #888; font-size: 10px;")

        # イベント接続
        self.slider.valueChanged.connect(self._on_slider_moved)

        layout.addWidget(self.value_label)
        layout.addWidget(self.slider)
        layout.addWidget(self.freq_label)

    def _on_slider_moved(self, value):
        self.value_label.setText(f"{value:+d}dB")
        # 「どの周波数が何dBになったか」をシグナルで飛ばす
        self.valueChanged.emit(self.frequency, value)

    def set_value(self, value):
        """プリセット選択時などに外部から値を設定する用"""
        self.slider.setValue(value)
