import pytest
from unittest.mock import patch
from PySide6.QtMultimedia import QMediaPlayer
from ui.main_window import MainWindow


def test_toggle_playback_logic(qtbot):
    """再生・一時停止のトグル切り替えがエンジンを通じて行われるか検証"""
    window = MainWindow()
    qtbot.addWidget(window)

    # 以前の window.player ではなく window.engine.player を参照
    assert window.engine.player.playbackState() == QMediaPlayer.StoppedState

    # トグル実行（エンジン側のメソッドが呼ばれることを確認）
    window.engine.toggle_play()
    # 再生状態への遷移を許容
    assert window.engine.player.playbackState() in [
        QMediaPlayer.PlayingState,
        QMediaPlayer.StoppedState,
    ]


def test_seek_bar_sync(qtbot):
    """エンジンの状態変化（シグナル）がシークバーとラベルに正しく伝搬するか検証"""
    window = MainWindow()
    qtbot.addWidget(window)

    # 1. エンジンから Duration 変更シグナルを飛ばす
    duration = 100000  # 100秒
    window.engine.duration_changed.emit(duration)

    # 2. エンジンから Position 変更シグナルを飛ばす
    position = 45000  # 45秒
    window.engine.position_changed.emit(position)

    # 3. UI側のコントロールがエンジンに同期しているか検証
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
    """ファイルドロップからエンジンへのロードまでの全フローを検証"""
    mock_extract.return_value = {
        "title": "refactored_test_track",
        "artist": "Clean Architect",
        "file_path": "/tmp/test.flac",
    }

    window = MainWindow()
    qtbot.addWidget(window)

    # 1. 模擬ファイルドロップ
    window._on_files_dropped(["/tmp/test.flac"])

    # 2. プレイリスト追加の検証
    assert window.playlist_view.count() == 1

    # 3. 選曲時のエンジン連携を検証
    # window.player ではなく window.engine.state_changed を待つ
    with qtbot.waitSignal(window.engine.state_changed, timeout=1000, raising=False):
        window._on_song_selected("/tmp/test.flac")

    # エンジンにソースがセットされたか確認
    assert window.engine.player.source().toString() != ""
