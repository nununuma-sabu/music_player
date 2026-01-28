from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QObject, Signal


class AudioEngine(QObject):
    """再生に関するロジックのみを担当するエンジン"""

    # UIに状態を伝えるためのシグナル
    position_changed = Signal(int)
    duration_changed = Signal(int)
    state_changed = Signal(QMediaPlayer.PlaybackState)
    metadata_updated = Signal(dict)

    # 新しいシグナル：メディアの状態（終了など）を通知
    media_status_changed = Signal(QMediaPlayer.MediaStatus)

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # メディア状態の変化を監視
        self.player.mediaStatusChanged.connect(self.media_status_changed.emit)

        # プレイヤーの信号をエンジンのシグナルへリレー
        self.player.positionChanged.connect(self.position_changed.emit)
        self.player.durationChanged.connect(self.duration_changed.emit)
        self.player.playbackStateChanged.connect(self.state_changed.emit)

    def load_song(self, file_path):
        self.player.setSource(file_path)
        self.player.play()

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def set_position(self, position):
        self.player.setPosition(position)

    # ボリューム設定
    def set_volume(self, value):
        """0-100の整数を受け取り、0.0-1.0に変換して適用"""
        # AudioEngine内で初期化済みのaudio_outputを使用
        self.audio_output.setVolume(value / 100.0)
