class PlaylistManager:
    """
    プレイリストのデータ（メタデータのリスト）を管理するクラス
    """

    def __init__(self):
        self._songs = []

    def add_song(self, metadata):
        """曲を追加する"""
        if metadata:
            self._songs.append(metadata)

    def get_all_songs(self):
        """現在の全リストを取得する"""
        return self._songs

    def remove_song(self, index):
        """指定したインデックスの曲を削除する"""
        if 0 <= index < len(self._songs):
            return self._songs.pop(index)
        return None

    def clear(self):
        """リストを空にする"""
        self._songs = []
