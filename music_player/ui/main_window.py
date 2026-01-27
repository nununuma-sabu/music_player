from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, Qt
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
        self.resize(800, 600)

        # データ管理の初期化
        self.playlist_manager = PlaylistManager()

        # メインレイアウトの設定
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # タブウィジェットの作成
        self.tabs = QTabWidget()

        # --- Playlist タブ ---
        self.playlist_container = QWidget()
        self.playlist_layout = QVBoxLayout(self.playlist_container)

        self.drop_zone = DropZone()
        self.playlist_view = PlaylistView()

        self.playlist_layout.addWidget(self.drop_zone)
        self.playlist_layout.addWidget(self.playlist_view)

        # --- Equalizer タブ ---
        self.eq_container = QWidget()
        self.eq_layout = QVBoxLayout(self.eq_container)
        self.eq_slider = EqSlider(frequency="1kHz")
        self.eq_layout.addWidget(self.eq_slider)

        self.tabs.addTab(self.playlist_container, "Playlist")
        self.tabs.addTab(self.eq_container, "Equalizer")

        # コントロールバー
        self.controls = PlayerControls()

        # メインレイアウトに配置
        self.main_layout.addWidget(self.tabs)
        self.main_layout.addWidget(self.controls)

        # 再生エンジン初期化
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)

        # シグナルとスロットの接続
        self.drop_zone.filesDropped.connect(self._on_files_dropped)

        self.controls.playClicked.connect(self.player.play)
        self.controls.pauseClicked.connect(self.player.pause)
        self.controls.stopClicked.connect(self.player.stop)

        # シークバーの同期接続
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.controls.seekRequested.connect(self.player.setPosition)

        # プレイリストの選曲シグナルを接続
        self.playlist_view.songSelected.connect(self._on_song_selected)

    def _on_files_dropped(self, files):
        """ファイルがドロップされた時の処理"""
        for f in files:
            metadata = extract_metadata(f)
            if metadata:
                self.playlist_manager.add_song(metadata)
                self.playlist_view.add_song_item(metadata)

    def _on_song_selected(self, file_path):
        """曲がダブルクリックされた時の処理"""
        metadata = extract_metadata(file_path)
        if metadata:
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.controls.update_song_info(metadata["title"], metadata["artist"])
            self.player.play()
            print(f"DEBUG: Playback started -> {file_path}")

    def _on_position_changed(self, position):
        """再生位置が変わるたびに呼ばれる"""
        self.controls.update_position(position, self.player.duration())

    def _on_duration_changed(self, duration):
        """曲が読み込まれて長さが確定した時に呼ばれる"""
        self.controls.set_duration(duration)
