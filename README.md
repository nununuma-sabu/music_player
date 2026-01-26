# Music Player (Provisional)

「車輪の再発明」を通じて、デジタルオーディオ信号処理とマルチ言語アーキテクチャを深く理解することを目的とした音楽再生アプリケーションです。

一般的な音楽プレイヤーが提供するデータベース管理機能をあえて排除し、「音の解析と加工（イコライザー）」という信号処理の核心部分に注力した設計を行っています。

---

## 🎨 コンセプト
- **適材適所のマルチ言語構成**: 高速な計算が必要な信号処理部はRust、柔軟なUI構築にはPython（PySide6）を採用。
- **信号処理の可視化**: 高速フーリエ変換（FFT）を用いたリアルタイム・スペクトラムアナライザーの実装。
- **ピュアなユーザー体験**: データベースレスな設計。ドラッグ＆ドロップによるオンメモリなキュー管理に特化。

---

## 🛠 技術スタック
- **GUI**: Python 3.x / PySide6 (Qt for Python)
- **Signal Processing Engine**: Rust (Planned: FFT, Equalizer)
- **Binding**: PyO3 (Python/Rust bridge)
- **Metadata**: Mutagen (ID3, Vorbis, etc.), Pillow (Image processing)
- **Environment**: WSL2 (Ubuntu) / Development target is Native App

---

## 🏗 アーキテクチャ
本プロジェクトでは、高レイヤ（UI）と低レイヤ（Engine）を明確に分離する疎結合な設計を採用しています。

### 1. Python Layer (Frontend)
- **PySide6**: ダークモードを基調としたネイティブUI。コンポーネント指向によるクラス設計。
- **Mutagen**: 音楽ファイルのタグ情報をオンメモリで解析。
- **SVG Icons**: OS環境（WSL/Windows/macOS）に依存しない、スケーラブルでシャープなグラフィック表現。

### 2. Rust Layer (Backend - Under Development)
- **Performance**: SIMD等を意識した高速な信号処理ロジック。
- **Algorithm**: 窓関数（Hann Window）を適用したFFT計算。
- **Bridge**: PyO3によるPythonモジュールとしての統合。

---

## 📈 現在の実装状況
- [x] PySide6を用いたダークモードGUIの構築
- [x] 各種コンポーネント（Slider, Controls, DropZone）のモジュール化
- [x] SVGアイコンによるUI/UXの改善
- [x] ファイルのドラッグ＆ドロップ検知
- [ ] Mutagenによるメタデータ表示の実装
- [ ] Rust製エンジンの統合
- [ ] リアルタイム・イコライザーの実装

---

## 🚀 セットアップ
```bash
# リポジトリのクローン
git clone [https://github.com/your-username/music_player.git](https://github.com/your-username/music_player.git)
cd music_player

# 依存ライブラリのインストール
pip install -r requirements.txt

# アプリケーションの起動
python main.py