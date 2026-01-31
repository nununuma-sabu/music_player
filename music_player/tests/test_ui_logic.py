import pytest
from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaPlayer
from unittest.mock import patch

# 修正箇所: music_player. プレフィックスを削除
from ui.main_window import MainWindow


@pytest.fixture
def window(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)
    return win


def test_initial_state(window):
    assert window.windowTitle() == "Music Player Portfolio"
    assert window.tabs.count() == 2


@patch("ui.main_window.extract_metadata")
def test_auto_play_next_song(mock_extract, qtbot):
    """再生終了時に自動で次の曲へ遷移するか検証"""
    mock_extract.side_effect = lambda f: {
        "title": f,
        "artist": "Artist",
        "file_path": f,
        "duration": 100,
    }

    win = MainWindow()
    qtbot.addWidget(win)
    win._on_files_dropped(["song1.mp3", "song2.mp3"])
    win.playlist_view.setCurrentRow(0)

    # 疑似的に EndOfMedia ステータスを送信
    win.engine.media_status_changed.emit(QMediaPlayer.MediaStatus.EndOfMedia)

    # currentRow が 1 に進んでいることを確認
    assert win.playlist_view.currentRow() == 1


@patch("ui.main_window.extract_metadata")
def test_manual_skip_logic(mock_extract, qtbot):
    """スキップボタンのクリックが正しくインデックス操作に繋がるか検証"""
    mock_extract.side_effect = lambda f: {
        "title": f,
        "artist": "Artist",
        "file_path": f,
        "duration": 100,
    }

    win = MainWindow()
    qtbot.addWidget(win)
    win._on_files_dropped(["song1.mp3", "song2.mp3"])
    win.playlist_view.setCurrentRow(0)

    # 進むボタン
    win.controls.skipForwardClicked.emit()
    assert win.playlist_view.currentRow() == 1

    # 戻るボタン
    win.controls.skipBackwardClicked.emit()
    assert win.playlist_view.currentRow() == 0
