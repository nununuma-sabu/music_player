from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from .components.eq_slider import EqSlider
from .components.player_controls import PlayerControls
from .components.drop_zone import DropZone
from .components.playlist_view import PlaylistView
from core.metadata import extract_metadata
from core.playlist import PlaylistManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Player Portfolio")
        self.resize(900, 650)  # タブ化により縦幅を最適化

        # マネージャーの初期化
        self.playlist_manager = PlaylistManager()

        # 中央ウィジェットとメインレイアウト
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # --- タブウィジェットの作成 ---
        self.tabs = QTabWidget()
        # スタイルシートでタブの見た目を少し調整
        self.tabs.setStyleSheet(
            """
            QTabWidget::pane { border: 1px solid #444; top: -1px; }
            QTabBar::tab { background: #2a2a2a; color: #aaa; padding: 10px 20px; border: 1px solid #444; }
            QTabBar::tab:selected { background: #333; color: #00d1b2; border-bottom: none; }
        """
        )

        # 1. Player Tab (Playlist + DropZone)
        player_tab = QWidget()
        player_layout = QVBoxLayout(player_tab)

        self.drop_zone = DropZone()
        self.drop_zone.filesDropped.connect(self._on_files_dropped)
        player_layout.addWidget(self.drop_zone)

        self.playlist_view = PlaylistView()
        player_layout.addWidget(self.playlist_view)

        # 2. Equalizer Tab
        eq_tab = QWidget()
        eq_layout = QHBoxLayout(eq_tab)
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
            band.valueChanged.connect(lambda f, v: print(f"EQ Change: {f} -> {v}dB"))
            eq_layout.addWidget(band)
            self.eq_bands[freq] = band

        # タブの追加
        self.tabs.addTab(player_tab, "Playlist")
        self.tabs.addTab(eq_tab, "Equalizer")

        main_layout.addWidget(self.tabs)

        # 3. 操作系（下部に固定）
        self.controls = PlayerControls()
        main_layout.addWidget(self.controls)

        # プレイリストの選曲シグナルを接続
        self.playlist_view.songSelected.connect(self._on_song_selected)

    def _on_files_dropped(self, files):
        for f in files:
            metadata = extract_metadata(f)
            if metadata:
                self.playlist_manager.add_song(metadata)
                self.playlist_view.add_song_item(metadata)

    def _on_song_selected(self, file_path):
        """曲がダブルクリックされた時の処理"""
        # メタデータを取得
        metadata = extract_metadata(file_path)

        if metadata:
            # 下部のコントロールバーの表示を更新
            self.controls.update_song_info(metadata["title"], metadata["artist"])
            print(f"DEBUG: UI Updated for -> {metadata['title']}")
