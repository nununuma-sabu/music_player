import numpy as np


def calculate_peaking_eq_coefficients(freq, sample_rate, gain_db, q=1.414):
    """
    ピーキングEQ（特定の周波数帯域を持ち上げる/下げるフィルタ）の
    デジタルフィルタ係数（b0, b1, b2, a1, a2）を算出します。

    Args:
        freq: 中心周波数 (Hz)
        sample_rate: サンプリングレート (Hz)
        gain_db: ゲイン (dB)
        q: Q値（帯域幅の鋭さ）

    Returns:
        np.ndarray: [b0, b1, b2, a1, a2] の5つの係数
    """
    # 中間パラメータの計算
    A = 10 ** (gain_db / 40.0)
    omega = 2.0 * np.pi * freq / sample_rate
    sn = np.sin(omega)
    cs = np.cos(omega)
    alpha = sn / (2.0 * q)

    # フィルタ係数の算出 (Robert Bristow-Johnson's Cookbook公式に基づく)
    b0 = 1.0 + alpha * A
    b1 = -2.0 * cs
    b2 = 1.0 - alpha * A
    a0 = 1.0 + alpha / A
    a1 = -2.0 * cs
    a2 = 1.0 - alpha / A

    # a0で正規化し、フィルタ演算に必要な5つの定数を返す
    # (a0が常に1になるよう正規化するのがデジタルフィルタの実装標準)
    return np.array([b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0])
