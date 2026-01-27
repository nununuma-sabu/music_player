import pytest
from PySide6.QtCore import Qt, QMimeData, QUrl, QPoint
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from ui.components.drop_zone import DropZone
from ui.components.playlist_view import PlaylistView


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
