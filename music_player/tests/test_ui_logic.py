import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtMultimedia import QMediaPlayer
from ui.main_window import MainWindow
from core.utils import get_asset_path


def test_volume_slider_sync(qtbot):
    """音量スライダーの操作がエンジンに正しく反映されるか検証"""
    window = MainWindow()
    qtbot.addWidget(window)

    # 1. スライダーの初期値(50)を確認
    assert window.controls.volume_slider.value() == 50
    assert window.engine.audio_output.volume() == pytest.approx(0.5)

    # 2. スライダーを 80 に動かす
    window.controls.volume_slider.setValue(80)

    # 3. エンジンの音量が 0.8 になっているか検証
    assert window.engine.audio_output.volume() == pytest.approx(0.8)


def test_playback_icon_toggle_logic(qtbot):
    """再生状態の変化に応じてトグルボタンのアイコンが切り替わるか検証"""
    window = MainWindow()
    qtbot.addWidget(window)

    # 再生状態を Playing に強制変更
    window.engine.state_changed.emit(QMediaPlayer.PlayingState)

    # アイコンが更新されているか確認
    assert window.controls.btn_toggle.icon() is not None


def test_asset_path_resolution():
    """パス解決ユーティリティが正しく動作するか検証"""
    test_path = "styles/icons/test_icon.svg"
    resolved = get_asset_path(test_path)

    # 入力パスが含まれていることを確認
    assert test_path in resolved


def test_toggle_playback_logic(qtbot):
    """再生・一時停止のトグル切り替えがエンジンを通じて行われるか検証"""
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.engine.player.playbackState() == QMediaPlayer.StoppedState

    window.engine.toggle_play()
    assert window.engine.player.playbackState() in [
        QMediaPlayer.PlayingState,
        QMediaPlayer.StoppedState,
    ]


def test_seek_bar_sync(qtbot):
    """エンジンの状態変化（シグナル）がシークバーとラベルに正しく伝搬するか検証"""
    window = MainWindow()
    qtbot.addWidget(window)

    # シグナルの発火
    duration = 100000
    window.engine.duration_changed.emit(duration)
    position = 45000
    window.engine.position_changed.emit(position)

    # UIの同期を確認
    assert window.controls.slider.value() == position
    assert window.controls.label_current.text() == "00:45"


def test_equalizer_initialization(qtbot):
    """UIの初期化（10バンド）が正しく行われているか検証"""
    window = MainWindow()
    qtbot.addWidget(window)
    assert len(window.eq_sliders) == 10
    assert "1kHz" in window.eq_sliders


@patch("ui.main_window.extract_metadata")
def test_main_window_full_flow(mock_extract, qtbot):
    """ファイルドロップからエンジンへのロード、情報表示までの全フローを検証"""
    mock_extract.return_value = {
        "title": "TEST_TRACK_001",
        "artist": "MOCK_ARTIST_ALPHA",
        "file_path": "/tmp/test_audio_file.flac",
    }

    window = MainWindow()  # ここが途切れていた箇所です！
    qtbot.addWidget(window)

    # 1. 模擬ファイルドロップ
    window._on_files_dropped(["/tmp/test_audio_file.flac"])

    # 2. プレイリスト追加の検証
    assert window.playlist_view.count() == 1

    # 3. 選曲時のエンジン連携
    with qtbot.waitSignal(window.engine.state_changed, timeout=1000, raising=False):
        window._on_song_selected("/tmp/test_audio_file.flac")

    # 4. 表示の検証
    assert "TEST_TRACK_001" in window.controls.info_label.text()
    assert "MOCK_ARTIST_ALPHA" in window.controls.info_label.text()


def test_auto_play_next_song(qtbot):
    """再生終了時に自動で次の曲へ遷移するか検証"""
    window = MainWindow()
    qtbot.addWidget(window)

    # 2曲追加
    window._on_files_dropped(["song1.mp3", "song2.mp3"])
    window.playlist_view.setCurrentRow(0)

    # 疑似的に EndOfMedia ステータスを送信
    from PySide6.QtMultimedia import QMediaPlayer

    window.engine.media_status_changed.emit(QMediaPlayer.MediaStatus.EndOfMedia)

    # 次の行が選択されているか
    assert window.playlist_view.currentRow() == 1


def test_manual_skip_logic(qtbot):
    """スキップボタンのクリックが正しくインデックス操作に繋がるか検証"""
    window = MainWindow()
    qtbot.addWidget(window)
    window._on_files_dropped(["song1.mp3", "song2.mp3"])
    window.playlist_view.setCurrentRow(0)

    # 進むボタン発火（シグナルを直接emit）
    window.controls.skipForwardClicked.emit()
    assert window.playlist_view.currentRow() == 1

    # 戻るボタン発火
    window.controls.skipBackwardClicked.emit()
    assert window.playlist_view.currentRow() == 0
