from PySide6.QtWidgets import QSlider, QStyle, QStyleOptionSlider, QToolTip
from PySide6.QtCore import Qt, Signal, QPoint


class ClickableSlider(QSlider):
    # ホバー位置の値(ms)とグローバル座標を送信するシグナル
    hoveredValue = Signal(int, QPoint)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        # ボタンを押していなくてもマウスの動きを検知するように設定
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        """マウス移動時にホバー位置の値を計算してシグナルを発火"""
        val = self._get_value_from_pos(event.position().toPoint())
        self.hoveredValue.emit(val, event.globalPosition().toPoint())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """マウスがスライダーから離れたらツールチップを隠す"""
        QToolTip.hideText()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """クリックした位置へジャンプする既存機能をリファクタリング"""
        if event.button() == Qt.LeftButton:
            new_value = self._get_value_from_pos(event.position().toPoint())
            self.setValue(new_value)
            self.sliderMoved.emit(new_value)
            event.accept()
        super().mousePressEvent(event)

    def _get_value_from_pos(self, pos):
        """座標からスライダーの値を計算する共通ロジック"""
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        sr = self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self
        )

        if self.orientation() == Qt.Horizontal:
            return QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(), pos.x() - sr.x(), sr.width()
            )
        else:
            return QStyle.sliderValueFromPosition(
                self.minimum(),
                self.maximum(),
                sr.height() - pos.y() + sr.y(),
                sr.height(),
            )
