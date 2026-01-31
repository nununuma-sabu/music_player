import pytest
from unittest.mock import patch
from PySide6.QtCore import Qt, QMimeData, QUrl, QPoint
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent
from ui.components.drop_zone import DropZone
from ui.components.playlist_view import PlaylistView
from ui.components.clickable_slider import ClickableSlider
from ui.components.player_controls import PlayerControls


def test_drop_zone_full_logic(qtbot):
    """DropZoneのドラッグ&ドロップイベントを全網羅"""
    widget = DropZone()
    qtbot.addWidget(widget)
    mime_valid = QMimeData()
    test_path = "/tmp/test_audio_01.flac"
    mime_valid.setUrls([QUrl.fromLocalFile(test_path)])
    event_enter = QDragEnterEvent(
        QPoint(0, 0), Qt.CopyAction, mime_valid, Qt.LeftButton, Qt.NoModifier
    )
    widget.dragEnterEvent(event_enter)
    assert event_enter.isAccepted()
    with qtbot.waitSignal(widget.filesDropped, timeout=1000) as blocker:
        event_drop = QDropEvent(
            QPoint(0, 0), Qt.CopyAction, mime_valid, Qt.LeftButton, Qt.NoModifier
        )
        widget.dropEvent(event_drop)
    assert test_path in blocker.args[0][0]


def test_playlist_view_interaction(qtbot):
    """PlaylistViewのアイテム追加とダブルクリック選択を検証"""
    view = PlaylistView()
    qtbot.addWidget(view)
    test_song_data = {
        "title": "Test_Track",
        "artist": "Mock",
        "file_path": "/path/test.flac",
    }
    view.add_song_item(test_song_data)
    assert view.count() == 1
    with qtbot.waitSignal(view.songSelected, timeout=1000) as blocker:
        view.itemDoubleClicked.emit(view.item(0))
    assert blocker.args[0] == "/path/test.flac"


# --- ここからが追加・修正したホバー関連のテスト ---


def test_clickable_slider_hover_signal(qtbot):
    """ClickableSlider がマウス移動時にホバー値を飛ばすか検証"""
    slider = ClickableSlider(Qt.Horizontal)
    slider.setRange(0, 100)
    slider.resize(200, 20)
    # CI(Xvfb)環境でイベントを届けるためのおまじない
    slider.show()
    qtbot.addWidget(slider)
    qtbot.waitExposed(slider)

    with qtbot.waitSignal(slider.hoveredValue, timeout=2000) as blocker:
        # スライダー中央(100px)付近をマウスが通過
        qtbot.mouseMove(slider, QPoint(100, 10))

    value, pos = blocker.args
    assert 40 <= value <= 60  # 中央付近の値か
    assert isinstance(pos, QPoint)


def test_player_controls_tooltip_logic(qtbot):
    """PlayerControls が適切なフォーマットでツールチップを出すか検証"""
    controls = PlayerControls()
    qtbot.addWidget(controls)

    # ガード節 (maximum > 0) を通すために範囲を設定
    controls.slider.setRange(0, 1000)
    controls.volume_slider.setRange(0, 100)

    # 1. 再生時間 (10秒 = 10000ms -> "00:10")
    # 定義元ではなく「利用元」をパッチするのがコツ
    with patch("ui.components.player_controls.QToolTip.showText") as mock_tooltip:
        controls._show_hover_time(10000, QPoint(0, 0))
        mock_tooltip.assert_called_once()
        assert mock_tooltip.call_args[0][1] == "00:10"

    # 2. ボリューム (80% -> "Vol: 80%")
    with patch("ui.components.player_controls.QToolTip.showText") as mock_tooltip:
        controls._show_hover_volume(80, QPoint(0, 0))
        mock_tooltip.assert_called_once()
        assert mock_tooltip.call_args[0][1] == "Vol: 80%"


def test_clickable_slider_direct_jump(qtbot):
    """クリック位置へのジャンプ機能の検証"""
    slider = ClickableSlider(Qt.Horizontal)
    slider.setRange(0, 100)
    slider.resize(200, 20)
    slider.show()
    qtbot.addWidget(slider)
    qtbot.waitExposed(slider)

    with qtbot.waitSignal(slider.sliderMoved, timeout=1000):
        qtbot.mouseClick(slider, Qt.LeftButton, pos=QPoint(100, 10))

    assert slider.value() > 0
