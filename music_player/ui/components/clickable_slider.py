from PySide6.QtWidgets import QSlider, QStyle, QStyleOptionSlider
from PySide6.QtCore import Qt


class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        # 左クリックの場合のみ「ジャンプ」させる
        if event.button() == Qt.LeftButton:
            # クリックされた位置から新しい値を計算
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            sr = self.style().subControlRect(
                QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self
            )

            # スライダーの向きに合わせて値をマッピング
            if self.orientation() == Qt.Horizontal:
                new_value = QStyle.sliderValueFromPosition(
                    self.minimum(),
                    self.maximum(),
                    event.position().toPoint().x() - sr.x(),
                    sr.width(),
                )
            else:
                new_value = QStyle.sliderValueFromPosition(
                    self.minimum(),
                    self.maximum(),
                    sr.height() - event.position().toPoint().y() + sr.y(),
                    sr.height(),
                )

            self.setValue(new_value)
            # 値が確定したので、シグナルを発生させて再生位置を飛ばす
            self.sliderMoved.emit(new_value)
            event.accept()

        # 親クラスのイベント（ドラッグ開始などのため）も呼んでおく
        super().mousePressEvent(event)
