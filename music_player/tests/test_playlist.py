import pytest
from core.playlist import PlaylistManager


@pytest.fixture
def manager():
    """テストごとに新しい PlaylistManager インスタンスを提供"""
    return PlaylistManager()


@pytest.fixture
def sample_metadata():
    """テスト用のサンプル楽曲データ"""
    return {
        "file_path": "/path/to/song.mp3",
        "title": "Test Song",
        "artist": "Test Artist",
        "album": "Test Album",
        "duration": 180,
    }


def test_add_song(manager, sample_metadata):
    # 曲を追加できるか
    manager.add_song(sample_metadata)
    songs = manager.get_all_songs()

    assert len(songs) == 1
    assert songs[0]["title"] == "Test Song"


def test_add_invalid_song(manager):
    # 無効なデータ（None）は追加されないか
    manager.add_song(None)
    assert len(manager.get_all_songs()) == 0


def test_remove_song(manager, sample_metadata):
    # 曲を削除できるか
    manager.add_song(sample_metadata)
    removed = manager.remove_song(0)

    assert removed["title"] == "Test Song"
    assert len(manager.get_all_songs()) == 0


def test_remove_invalid_index(manager, sample_metadata):
    # 範囲外のインデックス指定で正しく None を返すか
    manager.add_song(sample_metadata)
    removed = manager.remove_song(99)

    assert removed is None
    assert len(manager.get_all_songs()) == 1


def test_clear_playlist(manager, sample_metadata):
    # リストを空にできるか
    manager.add_song(sample_metadata)
    manager.add_song(sample_metadata)
    manager.clear()

    assert len(manager.get_all_songs()) == 0
