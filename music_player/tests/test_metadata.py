# tests/test_metadata.py
import pytest
from unittest.mock import MagicMock, patch
from core.metadata import extract_metadata


# --- MP3のテスト ---
def test_extract_metadata_mp3():
    # MutagenFile が返すオーディオオブジェクトのモック
    mock_audio = MagicMock()

    # ID3タグを模したモック。__contains__ を定義して "TIT2" in tags が True になるようにする
    tags_data = {
        "TIT2": ["Test MP3 Title"],
        "TPE1": ["Test MP3 Artist"],
        "TALB": ["Test MP3 Album"],
    }

    mock_tags = MagicMock()
    # .getall() の振る舞いを設定
    mock_tags.getall.side_effect = lambda key: tags_data.get(key, [])
    # インデックスアクセスや in 演算子のための設定
    mock_tags.__contains__.side_effect = lambda key: key in tags_data

    mock_audio.tags = mock_tags
    mock_audio.info.length = 180

    with patch("core.metadata.MutagenFile", return_value=mock_audio):
        info = extract_metadata("dummy.mp3")
        assert info is not None
        assert info["title"] == "Test MP3 Title"
        assert info["artist"] == "Test MP3 Artist"
        assert info["duration"] == 180


# --- FLACのテスト ---
def test_extract_metadata_flac():
    mock_audio = MagicMock()
    mock_audio.tags = {"title": ["Test FLAC Title"], "artist": ["Test FLAC Artist"]}
    mock_audio.info.length = 240

    with patch("core.metadata.MutagenFile", return_value=mock_audio):
        info = extract_metadata("dummy.flac")
        assert info["title"] == "Test FLAC Title"
        assert info["duration"] == 240


# --- タグがない場合のフォールバックテスト ---
def test_extract_metadata_no_tags():
    mock_audio = MagicMock()
    mock_audio.tags = None
    mock_audio.info.length = 100

    with patch("core.metadata.MutagenFile", return_value=mock_audio):
        info = extract_metadata("path/to/my_song.mp3")
        assert info["title"] == "my_song.mp3"
        assert info["artist"] == "Unknown Artist"


# --- 読み込みエラー時のテスト ---
def test_extract_metadata_error():
    with patch("core.metadata.MutagenFile", side_effect=Exception("Read Error")):
        info = extract_metadata("invalid.mp3")
        assert info is None


def test_extract_metadata_unrecognized_format():
    # mutagenが例外を出さずに None を返す（未対応フォーマット等）ケースのテスト
    # MutagenFile が None を返すようにモック
    with patch("core.metadata.MutagenFile", return_value=None):
        info = extract_metadata("unsupported.txt")
        assert info is None
