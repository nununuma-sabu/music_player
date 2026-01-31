import pytest
from unittest.mock import patch
from PySide6.QtCore import Qt, QMimeData, QUrl, QPoint, QEvent
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QContextMenuEvent
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


def test_clickable_slider_hover_and_leave(qtbot):
    """ホバー検知のタイムアウト対策を施したテスト"""
    slider = ClickableSlider(Qt.Horizontal)
    slider.setRange(0, 100)
    slider.resize(200, 20)
    slider.show()
    qtbot.addWidget(slider)
    qtbot.waitExposed(slider)

    # CI環境で確実に検知させるため、一度外から中へ移動させる
    qtbot.mouseMove(slider, QPoint(-1, -1))
    with qtbot.waitSignal(slider.hoveredValue, timeout=2000) as blocker:
        qtbot.mouseMove(slider, QPoint(100, 10))

    # ツールチップ非表示のパスも通す
    slider.leaveEvent(QEvent(QEvent.Leave))


def test_clickable_slider_vertical_calculation(qtbot):
    """垂直方向の座標計算の修正"""
    slider = ClickableSlider(Qt.Vertical)
    slider.setRange(0, 100)
    slider.resize(20, 200)
    slider.show()
    qtbot.addWidget(slider)
    qtbot.waitExposed(slider)

    # 垂直スライダー: Y=0付近（上）が最大値、Y=200付近（下）が最小値
    # 修正: 上の方(20px)をクリックして 80 以上の値になるか確認
    qtbot.mouseClick(slider, Qt.LeftButton, pos=QPoint(10, 20))
    assert slider.value() > 80


def test_player_controls_tooltip_display(qtbot):
    """PlayerControls が適切な文字列でツールチップを表示するか検証"""
    controls = PlayerControls()
    qtbot.addWidget(controls)

    # ロジックを通すために最大値を設定
    controls.slider.setRange(0, 1000)

    # 1. 再生時間ホバー
    with patch("PySide6.QtWidgets.QToolTip.showText") as mock_tooltip:
        controls._show_hover_time(500, QPoint(0, 0))
        mock_tooltip.assert_called_once()
        assert "00:00" in mock_tooltip.call_args[0][1]

    # 2. ボリュームホバー
    with patch("PySide6.QtWidgets.QToolTip.showText") as mock_tooltip:
        controls._show_hover_volume(80, QPoint(0, 0))
        mock_tooltip.assert_called_once()
        assert "Vol: 80%" == mock_tooltip.call_args[0][1]


def test_playlist_view_context_menu_with_item(qtbot):
    """アイテムが存在する状態でのコンテキストメニュー動作を検証"""
    view = PlaylistView()
    view.resize(200, 200)
    view.show()
    qtbot.addWidget(view)
    qtbot.waitExposed(view)

    # アイテムを追加
    view.add_song_item({"title": "Test", "artist": "Artist", "file_path": "path"})

    # アイテムがある場所（上端付近）を右クリック
    from PySide6.QtGui import QContextMenuEvent

    event = QContextMenuEvent(QContextMenuEvent.Mouse, QPoint(10, 10), QPoint(10, 10))

    # 実行してもハングアップしない（menu.popup() を使っているため）ことを確認
    view.contextMenuEvent(event)


def test_playlist_view_full_coverage(qtbot):
    """PlaylistView の未通過ロジック（右クリック・キー操作）を網羅"""
    view = PlaylistView()
    view.resize(200, 200)
    view.show()
    qtbot.addWidget(view)

    # アイテムを追加
    song = {"title": "Test", "artist": "Artist", "file_path": "path.mp3"}
    view.add_song_item(song)

    # 1. アイテム上での右クリックイベント
    # アイテムが存在する座標（1行目の中心あたり）を狙う
    item_rect = view.visualItemRect(view.item(0))
    pos = item_rect.center()
    event = QContextMenuEvent(QContextMenuEvent.Mouse, pos, view.mapToGlobal(pos))
    view.contextMenuEvent(event)  # menu.popup() なのでブロックされない

    # 2. Deleteキーによる削除
    view.setCurrentRow(0)
    with qtbot.waitSignal(view.songDeleted, timeout=1000) as blocker:
        qtbot.keyClick(view, Qt.Key_Delete)
    assert blocker.args[0] == 0


def test_player_controls_tooltip_logic_fix(qtbot):
    """PlayerControls のツールチップ表示条件を網羅"""
    controls = PlayerControls()
    qtbot.addWidget(controls)

    # ガード節 maximum > 0 を通す設定
    controls.slider.setRange(0, 1000)

    with patch("ui.components.player_controls.QToolTip.showText") as mock_tooltip:
        # 再生時間表示
        controls._show_hover_time(60000, QPoint(0, 0))
        mock_tooltip.assert_called_with(QPoint(0, 0), "01:00", controls.slider)
