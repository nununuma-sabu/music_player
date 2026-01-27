from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
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
        # タブ全体の背景も念のため指定
        self.tabs.setStyleSheet(
            """
            /* タブが表示される土台の部分 */
            QTabWidget::pane {
                border: none;
                background-color: #121212;
                top: -1px;
            }
            /* タブバー全体の背景 */
            QTabBar {
                background-color: #2a2a2a;
            }
            /* 個々のタブ（非選択時） */
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #888888;
                padding: 10px 30px;
                border: none;
                min-width: 80px;
            }
            /* マウスを乗せた時 */
            QTabBar::tab:hover {
                background-color: #333333;
                color: #ffffff;
            }
            /* ★ 選択されているタブ ★ */
            QTabBar::tab:selected {
                background-color: #121212; /* コンテンツエリアと同じ黒 */
                color: #00f2c3;            /* ぬまお気に入りのミントグリーン */
                border-bottom: 3px solid #00f2c3; /* 下線で強調 */
                font-weight: bold;
            }
        """
        )

        # --- Playlist タブ ---
        self.playlist_container = QWidget()
        self.playlist_layout = QVBoxLayout(self.playlist_container)

        self.drop_zone = DropZone()
        self.playlist_view = PlaylistView()

        self.playlist_layout.addWidget(self.drop_zone)
        self.playlist_layout.addWidget(self.playlist_view)

        # --- Equalizer タブ ---
        self.eq_container = QWidget()
        self.eq_container.setObjectName("eqContainer")

        # 【解決の鍵1】属性を有効化
        self.eq_container.setAttribute(Qt.WA_StyledBackground)
        # 【解決の鍵2】インラインスタイルで強制的に背景を黒くし、中身のSliderも透かす
        self.eq_container.setStyleSheet(
            """
            #eqContainer { 
                background-color: #121212; 
            }
            QWidget { 
                background-color: transparent; 
            }
        """
        )

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
        self.controls.playPauseClicked.connect(self._toggle_playback)
        self.controls.stopClicked.connect(self.player.stop)
        self.player.playbackStateChanged.connect(self.controls.update_playback_icons)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.controls.seekRequested.connect(self.player.setPosition)
        self.playlist_view.songSelected.connect(self._on_song_selected)

    def _toggle_playback(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _on_files_dropped(self, files):
        for f in files:
            metadata = extract_metadata(f)
            if metadata:
                self.playlist_manager.add_song(metadata)
                self.playlist_view.add_song_item(metadata)

    def _on_song_selected(self, file_path):
        metadata = extract_metadata(file_path)
        if metadata:
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.controls.update_song_info(metadata["title"], metadata["artist"])
            self.player.play()

    def _on_position_changed(self, position):
        self.controls.update_position(position, self.player.duration())

    def _on_duration_changed(self, duration):
        self.controls.set_duration(duration)
