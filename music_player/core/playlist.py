class PlaylistManager:
    """プレイリストのデータ管理を担当するクラス"""

    def __init__(self):
        self.songs = []

    def add_song(self, metadata):
        """楽曲を追加（Noneや無効なデータはスキップ）"""
        # バリデーションを追加してテストをパスさせる
        if metadata is None or not isinstance(metadata, dict):
            return
        self.songs.append(metadata)

    def remove_song(self, index):
        """指定したインデックスの楽曲をリストから削除"""
        if 0 <= index < len(self.songs):
            return self.songs.pop(index)
        return None

    def clear(self):
        """プレイリストを空にする（テストの期待値に合わせて名称変更）"""
        self.songs = []

    def get_all_songs(self):
        """全楽曲リストを取得"""
        return self.songs
