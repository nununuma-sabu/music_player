from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QObject, Signal


class AudioEngine(QObject):
    """再生に関するロジックのみを担当するエンジン"""

    # UIに状態を伝えるためのシグナル
    position_changed = Signal(int)
    duration_changed = Signal(int)
    state_changed = Signal(QMediaPlayer.PlaybackState)
    metadata_updated = Signal(dict)

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

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
