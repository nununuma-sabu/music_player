from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from .components.eq_slider import EqSlider
from .components.player_controls import PlayerControls
from .components.drop_zone import DropZone


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Player Portfolio")
        self.resize(900, 600)

        # 中央ウィジェットとメインレイアウト
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 1. ドロップエリア（上部）
        self.drop_zone = DropZone()
        self.drop_zone.filesDropped.connect(self._on_files_dropped)
        main_layout.addWidget(self.drop_zone)

        # 2. イコライザーエリア（中部）
        eq_group = QWidget()
        eq_layout = QHBoxLayout(eq_group)
        self.eq_bands = {}
        frequencies = [
            "32Hz",
            "64Hz",
            "125Hz",
            "250Hz",
            "500Hz",
            "1kHz",
            "2kHz",
            "4kHz",
            "8kHz",
            "16kHz",
        ]

        for freq in frequencies:
            band = EqSlider(freq)
            # スライダーが動いたらとりあえずコンソールに出力
            band.valueChanged.connect(lambda f, v: print(f"EQ Change: {f} -> {v}dB"))
            eq_layout.addWidget(band)
            self.eq_bands[freq] = band

        main_layout.addWidget(eq_group)

        # 3. 操作系（下部）
        self.controls = PlayerControls()
        self.controls.playClicked.connect(lambda: print("Play Clicked"))
        main_layout.addWidget(self.controls)

    def _on_files_dropped(self, files):
        for f in files:
            print(f"Dropped: {f}")
        # ここで将来的にプレイリストへの追加処理を行う
