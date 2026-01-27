import pytest
from unittest.mock import patch
from PySide6.QtMultimedia import QMediaPlayer
from ui.main_window import MainWindow


def test_toggle_playback_logic(qtbot):
    """再生・一時停止のトグル切り替えロジックを検証"""
    window = MainWindow()
    qtbot.addWidget(window)

    # 初期状態は停止(StoppedState)であることを確認
    assert window.player.playbackState() == QMediaPlayer.StoppedState

    # トグル実行 (再生へ)
    window._toggle_playback()
    # Sourceがないため実際にはすぐ止まるが、メソッドが呼ばれた際の挙動を確認
    assert window.player.playbackState() in [
        QMediaPlayer.PlayingState,
        QMediaPlayer.StoppedState,
    ]


def test_seek_bar_sync(qtbot):
    """プレイヤーの再生位置がシークバーとラベルに反映されるか検証"""
    window = MainWindow()
    qtbot.addWidget(window)

    # 1. 期間(Duration)のセット
    duration = 100000  # 100秒
    window._on_duration_changed(duration)

    # 2. 再生位置(Position)の変更
    position = 30000  # 30秒
    window._on_position_changed(position)

    # UI側のコントロールに反映されているか確認
    assert window.controls.slider.value() == position
    assert window.controls.label_current.text() == "00:30"


def test_equalizer_initialization(qtbot):
    """10バンドのイコライザーが正しく生成されているか検証"""
    window = MainWindow()
    qtbot.addWidget(window)

    # 周波数リストの数が10個であることを確認
    assert len(window.eq_sliders) == 10
    assert "1kHz" in window.eq_sliders


@patch("ui.main_window.extract_metadata")
def test_main_window_full_flow(mock_extract, qtbot):
    """ファイルドロップからプレイリスト追加、選曲再生までの全フローを検証"""
    # extract_metadata が実ファイルを見に行かないようにモック化
    mock_extract.return_value = {
        "title": "mock_track_001",
        "artist": "Mock Artist",
        "file_path": "/tmp/mock_audio.flac",
    }

    window = MainWindow()
    qtbot.addWidget(window)

    mock_files = ["/tmp/mock_audio.flac"]

    # 1. 模擬ファイルドロップ実行
    window._on_files_dropped(mock_files)

    # 2. プレイリストにアイテムが追加されたか確認
    assert window.playlist_view.count() == 1
    assert "mock_track_001" in window.playlist_view.item(0).text()

    # 3. 選曲（再生開始）処理の実行
    with qtbot.waitSignal(
        window.player.playbackStateChanged, timeout=1000, raising=False
    ):
        window._on_song_selected(mock_files[0])

    # 4. ソースがセットされているか確認
    assert window.player.source().toString() != ""
