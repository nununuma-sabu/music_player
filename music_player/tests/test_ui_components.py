import pytest
from PySide6.QtCore import Qt, QMimeData, QUrl, QPoint
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from ui.components.drop_zone import DropZone
from ui.components.playlist_view import PlaylistView
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import QPoint, Qt
from ui.components.clickable_slider import ClickableSlider


def test_drop_zone_full_logic(qtbot):
    """DropZoneのドラッグ&ドロップイベントを全網羅"""
    widget = DropZone()
    qtbot.addWidget(widget)

    # 1. 有効な拡張子（.flac）の模擬データをドラッグ
    mime_valid = QMimeData()
    test_path = "/tmp/test_audio_01.flac"
    mime_valid.setUrls([QUrl.fromLocalFile(test_path)])

    event_enter = QDragEnterEvent(
        QPoint(0, 0), Qt.CopyAction, mime_valid, Qt.LeftButton, Qt.NoModifier
    )
    widget.dragEnterEvent(event_enter)
    assert event_enter.isAccepted()  # 有効なファイルが受け入れられるか検証

    # 2. 実際にドロップした時のシグナル発火を検証
    with qtbot.waitSignal(widget.filesDropped, timeout=1000) as blocker:
        event_drop = QDropEvent(
            QPoint(0, 0), Qt.CopyAction, mime_valid, Qt.LeftButton, Qt.NoModifier
        )
        widget.dropEvent(event_drop)

    assert test_path in blocker.args[0][0]  # 正しいパスがシグナルで飛んでいるか

    # 3. 無効なデータ（テキストデータ等）の拒絶を検証
    mime_invalid = QMimeData()
    mime_invalid.setText("invalid_test_data")
    event_invalid = QDragEnterEvent(
        QPoint(0, 0), Qt.CopyAction, mime_invalid, Qt.LeftButton, Qt.NoModifier
    )
    widget.dragEnterEvent(event_invalid)
    assert not event_invalid.isAccepted()  # ファイル以外が拒絶されるか


def test_playlist_view_interaction(qtbot):
    """PlaylistViewのアイテム追加とダブルクリック選択を検証"""
    view = PlaylistView()
    qtbot.addWidget(view)

    # テスト用ダミーデータ
    test_song_data = {
        "title": "Test_Track_Title_001",
        "artist": "Mock_Artist_Alpha",
        "file_path": "/home/user/music/test_unit.flac",
    }

    # 1. アイテム追加ロジックの通過
    view.add_song_item(test_song_data)
    assert view.count() == 1
    assert "Test_Track_Title_001" in view.item(0).text()  # 表示内容の整合性

    # 2. ダブルクリックによる選曲イベントの検証
    with qtbot.waitSignal(view.songSelected, timeout=1000) as blocker:
        # 内部のシグナルを手動で発行し、スロットへの繋がりを確認
        view.itemDoubleClicked.emit(view.item(0))

    assert (
        blocker.args[0] == "/home/user/music/test_unit.flac"
    )  # パスが正しく伝搬したか


def test_clickable_slider_direct_jump(qtbot):
    """シークバーのクリック位置へ正しく値がジャンプするかを検証"""
    # 1. 横向きのスライダーを作成 (範囲: 0 - 100)
    slider = ClickableSlider(Qt.Horizontal)
    slider.setRange(0, 100)
    slider.setFixedWidth(100)  # 計算を単純にするため幅を固定
    qtbot.addWidget(slider)

    # 2. スライダーの中央（50px地点）をクリックしたことにする
    click_point = QPoint(50, slider.height() // 2)

    # sliderMoved シグナル（再生位置変更のトリガー）が発火するか監視
    with qtbot.waitSignal(slider.sliderMoved, timeout=1000) as blocker:
        # 左クリックをシミュレート
        qtbot.mouseClick(slider, Qt.LeftButton, pos=click_point)

    # 3. 値が中央付近（50）にジャンプしているか検証
    # スタイルの余白等により多少の前後があるため、範囲で検証
    assert 45 <= slider.value() <= 55
    assert 45 <= blocker.args[0] <= 55


def test_playlist_view_delete_key(qtbot):
    """Deleteキーによる削除シグナル発火を検証"""
    view = PlaylistView()
    qtbot.addWidget(view)

    # テストデータ追加
    view.add_song_item({"title": "DeleteMe", "artist": "Artist", "file_path": "path"})
    view.setCurrentRow(0)

    # Deleteキー押下時に songDeleted シグナルが飛ぶか
    with qtbot.waitSignal(view.songDeleted, timeout=1000) as blocker:
        qtbot.keyClick(view, Qt.Key_Delete)

    assert blocker.args[0] == 0


def test_playlist_view_context_menu(qtbot):
    """右クリックメニュー（コンテキストメニュー）イベントの通過を検証"""
    view = PlaylistView()
    qtbot.addWidget(view)
    view.add_song_item({"title": "MenuTest", "artist": "Artist", "file_path": "path"})

    # メニューイベントを直接呼び出し（正常終了を確認）
    from PySide6.QtGui import QContextMenuEvent

    event = QContextMenuEvent(QContextMenuEvent.Mouse, QPoint(5, 5), QPoint(5, 5))
    view.contextMenuEvent(event)  # エラーが出ないことの確認


from unittest.mock import patch
from ui.components.player_controls import PlayerControls


def test_clickable_slider_hover_signal(qtbot):
    """ClickableSlider がマウス移動時に正しい値をシグナルで飛ばすか検証"""
    slider = ClickableSlider(Qt.Horizontal)
    slider.setRange(0, 100)
    slider.resize(200, 20)
    # CI環境（xvfb等）でイベントを確実に届けるため、表示して描画を待機
    slider.show()
    qtbot.addWidget(slider)
    qtbot.waitExposed(slider)

    # タイムアウトを少し伸ばしてシグナルを待機
    with qtbot.waitSignal(slider.hoveredValue, timeout=2000) as blocker:
        qtbot.mouseMove(slider, QPoint(100, 10))

    value, pos = blocker.args
    assert isinstance(value, int)
    assert 0 <= value <= 100
    assert isinstance(pos, QPoint)


def test_player_controls_tooltip_logic(qtbot):
    """PlayerControls がスライダーの値に応じて正しい文字列をツールチップに出すか検証"""
    controls = PlayerControls()
    qtbot.addWidget(controls)

    # 実装側の `maximum() > 0` 判定を通すために範囲を設定
    controls.slider.setRange(0, 100000)
    controls.volume_slider.setRange(0, 100)

    # 1. 再生時間の表示ロジック (1分 = 60000ms)
    # パッチ対象を「利用されている場所」に変更
    with patch("ui.components.player_controls.QToolTip.showText") as mock_tooltip:
        controls._show_hover_time(60000, QPoint(10, 10))
        # メソッドが呼ばれたことを確認
        mock_tooltip.assert_called_once()
        # 第2引数の文字列がフォーマットされているか検証
        args = mock_tooltip.call_args[0]
        assert args[1] == "01:00"

    # 2. 音量の表示ロジック
    with patch("ui.components.player_controls.QToolTip.showText") as mock_tooltip:
        controls._show_hover_volume(50, QPoint(20, 20))
        mock_tooltip.assert_called_once()
        args = mock_tooltip.call_args[0]
        assert args[1] == "Vol: 50%"


def test_slider_jump_on_click(qtbot):
    """スライダーをクリックした時に値がジャンプするか検証"""
    slider = ClickableSlider(Qt.Horizontal)
    slider.setRange(0, 100)
    slider.resize(200, 20)
    slider.setValue(0)
    slider.show()
    qtbot.addWidget(slider)
    qtbot.waitExposed(slider)

    # 中央をクリック
    qtbot.mouseClick(slider, Qt.LeftButton, pos=QPoint(100, 10))
    # 値が初期値の 0 から更新されているか確認
    assert slider.value() > 0
