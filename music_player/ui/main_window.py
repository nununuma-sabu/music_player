from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QIcon
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

        # アプリケーションアイコンの設定
        icon_path = get_asset_path("styles/icons/app_icon.png")
        self.setWindowIcon(QIcon(icon_path))

        # 1. ロジック・データ管理の初期化
        self.playlist_manager = PlaylistManager()
        self.engine = AudioEngine()

        # 2. UIコンポーネントの構築
        self._init_ui()

        # 3. スタイルの適用
        self._apply_styles()

        # 4. シグナルとスロットの接続
        self._setup_connections()

    def _init_ui(self):
        """UIの配置とレイアウト構築を担当"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # タブウィジェット
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

        # コントロールバー
        self.controls = PlayerControls()

        # メイン配置
        self.main_layout.addWidget(self.tabs)
        self.main_layout.addWidget(self.controls)

    def _apply_styles(self):
        """強制スタイリングの一括管理"""
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
            """
            #eqContainer { background-color: #121212; }
            QWidget { background-color: transparent; }
        """
        )

    def _setup_connections(self):
        """UIとエンジン、各コンポーネント間の連携を定義"""
        # ファイルドロップ連携
        self.drop_zone.filesDropped.connect(self._on_files_dropped)
        self.playlist_view.songSelected.connect(self._on_song_selected)

        # プレイヤーコントロール -> エンジン
        self.controls.playPauseClicked.connect(self.engine.toggle_play)
        self.controls.stopClicked.connect(self.engine.player.stop)
        self.controls.seekRequested.connect(self.engine.set_position)

        # エンジン -> UI状態同期
        self.engine.state_changed.connect(self.controls.update_playback_icons)
        self.engine.position_changed.connect(self._on_position_changed)
        self.engine.duration_changed.connect(self.controls.set_duration)

        # 音量スライダーの変更をエンジンに伝える
        self.controls.volume_slider.valueChanged.connect(self.engine.set_volume)

        # ★ 起動時のスライダー値をエンジンに即時反映させる
        self.engine.set_volume(self.controls.volume_slider.value())

        # Deleteキー・右クリック共通の削除処理を接続
        self.playlist_view.songDeleted.connect(self._on_delete_song)

    def _on_files_dropped(self, files):
        """ファイルが選択・ドロップされた時の処理"""
        if not files:
            return

        # 今回追加された曲の中の「最初の有効な曲」を即再生するためのフラグ
        first_valid_metadata = None
        # 追加前のプレイリストの末尾インデックスを保持
        start_row = self.playlist_view.count()

        for f in files:
            metadata = extract_metadata(f)
            if metadata:
                self.playlist_manager.add_song(metadata)
                self.playlist_view.add_song_item(metadata)
                # 最初に読み込みに成功した曲を保持しておく
                if first_valid_metadata is None:
                    first_valid_metadata = metadata

        # 仕様に基づき、選択された楽曲の1曲目を即再生する
        if first_valid_metadata:
            self.engine.load_song(first_valid_metadata["file_path"])
            self.controls.update_song_info(
                first_valid_metadata["title"], first_valid_metadata["artist"]
            )
            # UI側のハイライトを追加された曲の先頭に合わせる
            self.playlist_view.setCurrentRow(start_row)

    def _on_song_selected(self, file_path):
        """プレイリストで曲が選択された時の処理"""
        metadata = extract_metadata(file_path)
        if metadata:
            self.engine.load_song(file_path)
            self.controls.update_song_info(metadata["title"], metadata["artist"])

    def _on_position_changed(self, position):
        """再生位置が変更された時のUI更新"""
        self.controls.update_position(position, self.engine.player.duration())

    def _on_delete_song(self, index):
        """プレイリストから曲を削除する処理"""
        # 1. データモデルから削除
        removed_song = self.playlist_manager.remove_song(index)

        if removed_song:
            # 2. UI表示（QListWidget）から削除
            self.playlist_view.takeItem(index)

            # 3. 削除した曲が今再生中の曲だった場合の処理（任意）
            # 必要に応じて停止させる、あるいは次の曲へ移るロジックを追加できます
            print(f"Deleted: {removed_song.get('title')}")
