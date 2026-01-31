from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QMediaPlayer
from .components.eq_slider import EqSlider
from .components.player_controls import PlayerControls
from .components.drop_zone import DropZone
from .components.playlist_view import PlaylistView
from core.metadata import extract_metadata
from core.playlist import PlaylistManager
from core.engine import AudioEngine
from core.utils import get_asset_path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Player Portfolio")
        self.resize(800, 600)

        icon_path = get_asset_path("styles/icons/app_icon.png")
        self.setWindowIcon(QIcon(icon_path))

        self.playlist_manager = PlaylistManager()
        self.engine = AudioEngine()

        self._init_ui()
        self._apply_styles()
        self._setup_connections()

    def _init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()

        # Playlist タブ
        self.playlist_container = QWidget()
        self.playlist_layout = QVBoxLayout(self.playlist_container)
        self.drop_zone = DropZone()
        self.playlist_view = PlaylistView()
        self.playlist_layout.addWidget(self.drop_zone)
        self.playlist_layout.addWidget(self.playlist_view)

        # Equalizer タブ
        self.eq_container = QWidget()
        self.eq_container.setObjectName("eqContainer")
        self.eq_container.setAttribute(Qt.WA_StyledBackground)
        self.eq_layout = QHBoxLayout(self.eq_container)
        self.eq_layout.setContentsMargins(20, 20, 20, 20)
        self.eq_layout.setSpacing(10)

        frequencies = [
            "31Hz",
            "62Hz",
            "125Hz",
            "250Hz",
            "500Hz",
            "1kHz",
            "2kHz",
            "4kHz",
            "8kHz",
            "16kHz",
        ]
        self.eq_sliders = {}
        for freq in frequencies:
            slider = EqSlider(frequency=freq)
            self.eq_layout.addWidget(slider)
            self.eq_sliders[freq] = slider

        self.tabs.addTab(self.playlist_container, "Playlist")
        self.tabs.addTab(self.eq_container, "Equalizer")

        self.controls = PlayerControls()
        self.main_layout.addWidget(self.tabs)
        self.main_layout.addWidget(self.controls)

    def _apply_styles(self):
        self.tabs.setStyleSheet(
            """
            QTabWidget::pane { border: none; background-color: #121212; top: -1px; }
            QTabBar { background-color: #2a2a2a; }
            QTabBar::tab { background-color: #2a2a2a; color: #888888; padding: 10px 30px; border: none; min-width: 80px; }
            QTabBar::tab:hover { background-color: #333333; color: #ffffff; }
            QTabBar::tab:selected { background-color: #121212; color: #00f2c3; border-bottom: 3px solid #00f2c3; font-weight: bold; }
        """
        )
        self.eq_container.setStyleSheet(
            "#eqContainer { background-color: #121212; } QWidget { background-color: transparent; }"
        )

    def _setup_connections(self):
        self.drop_zone.filesDropped.connect(self._on_files_dropped)
        self.playlist_view.songSelected.connect(self._on_song_selected)
        self.playlist_view.songDeleted.connect(self._on_delete_song)

        self.controls.playPauseClicked.connect(self.engine.toggle_play)
        self.controls.stopClicked.connect(self.engine.player.stop)
        self.controls.seekRequested.connect(self.engine.set_position)

        # 進む・戻るボタンの接続
        self.controls.skipForwardClicked.connect(self._play_next_song)
        self.controls.skipBackwardClicked.connect(self._play_prev_song)

        self.engine.state_changed.connect(self.controls.update_playback_icons)
        self.engine.position_changed.connect(self._on_position_changed)
        self.engine.duration_changed.connect(self.controls.set_duration)
        self.engine.media_status_changed.connect(self._on_media_status_changed)

        self.controls.volume_slider.valueChanged.connect(self.engine.set_volume)
        self.engine.set_volume(self.controls.volume_slider.value())

    def _on_files_dropped(self, files):
        if not files:
            return
        start_row = self.playlist_view.count()
        first_valid_metadata = None

        for f in files:
            metadata = extract_metadata(f)
            if metadata:
                self.playlist_manager.add_song(metadata)
                self.playlist_view.add_song_item(metadata)
                if first_valid_metadata is None:
                    first_valid_metadata = metadata

        if first_valid_metadata:
            self._play_song_at_path(first_valid_metadata["file_path"])
            self.playlist_view.setCurrentRow(start_row)

    def _on_song_selected(self, file_path):
        self._play_song_at_path(file_path)

    def _play_song_at_path(self, file_path):
        """再生とUI更新の共通処理"""
        metadata = extract_metadata(file_path)
        if metadata:
            self.engine.load_song(file_path)
            self.controls.update_song_info(metadata["title"], metadata["artist"])

    def _on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._play_next_song()

    def _play_next_song(self):
        count = self.playlist_view.count()
        if count == 0:
            return
        next_row = (self.playlist_view.currentRow() + 1) % count
        self._play_at_index(next_row)

    def _play_prev_song(self):
        count = self.playlist_view.count()
        if count == 0:
            return
        prev_row = (self.playlist_view.currentRow() - 1 + count) % count
        self._play_at_index(prev_row)

    def _play_at_index(self, index):
        self.playlist_view.setCurrentRow(index)
        item = self.playlist_view.item(index)
        if item:
            self._play_song_at_path(item.data(Qt.UserRole))

    def _on_delete_song(self, index):
        self.playlist_manager.remove_song(index)
        self.playlist_view.takeItem(index)

    def _on_position_changed(self, position):
        self.controls.update_position(position, self.engine.player.duration())
