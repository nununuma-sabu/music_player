# Music Player (Provisional)

![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/nununuma-sabu/2ee8e15cec07f3ec79161c23e9e0c25e/raw/music-player-coverage.json)
![Tests](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/nununuma-sabu/2ee8e15cec07f3ec79161c23e9e0c25e/raw/music-player-tests.json)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

「車輪の再発明」を通じて、デジタルオーディオ信号処理（DSP）と Python による高度な GUI 構築を追求する音楽再生アプリケーションです。

一般的な音楽プレイヤーの利便性以上に、「音そのものの解析と加工」というエンジニアリングの核心に注力した設計を行っています。

---

## 🎨 コンセプト
- **デジタル信号処理（DSP）の探求**: NumPyを活用した高速な周波数解析。将来的には Numba による JIT コンパイルを用いたリアルタイムフィルタリングの実装を目指しています。
- **テスタビリティの追求**: ロジックと表示を厳密に分離。複雑な GUI コンポーネントを含め、90% 以上のユニットテストカバレッジを維持しています。
- **拡張可能なアーキテクチャ**: プラグイン感覚でエフェクトや解析アルゴリズムを追加できる、疎結合な設計を採用しています。

---

## 🛠 技術スタック
- **GUI**: PySide6 (Qt for Python)
- **Signal Processing**: 
    - **NumPy**: 高速なベクトル演算による信号解析。
    - **FFT (Fast Fourier Transform)**: リアルタイムなスペクトラム解析の基盤。
- **Metadata**: Mutagen (MP3 / FLAC / OGG / アルバムアート抽出対応)
- **Quality Assurance**: pytest / coverage (カバレッジ 90% 達成)

---

## 🏗 アーキテクチャ

### 1. Presentation Layer (UI)
- **Component-based**: 再生コントロール、プレイリスト、視覚化ウィジェット等を独立したコンポーネントとして構築。
- **Custom Styling**: QSS（Qt Style Sheets）によるモダンなダークモード・デザイン。

### 2. Core & DSP Layer
- **Audio Engine**: `QtMultimedia` をベースとした、堅牢な再生制御。
- **Spectrum Analyzer**: ハニング窓の適用および対数スケール変換を伴う、FFT 解析エンジン。
- **Filter Assets**: 独自のバイカッド・フィルタ設計ロジック（Peaking EQ等）を技術資産として保有。

---

## 📈 現在の実装状況
- [x] PySide6 によるモダンなダークモード GUI
- [x] プレイリストの動的管理（~~ドラッグ＆ドロップ~~、ファイルダイアログ、自動連続再生）
- [x] アルバムアート・メタデータの高度な抽出・表示
- [x] 90% の高いユニットテスト網羅率による品質担保
- [x] **FFT（高速フーリエ変換）を用いた周波数解析エンジンの実装**
- [ ] 解析結果の GUI へのリアルタイム描画（スペクトラムビジュアライザー）
- [ ] 10バンド・イコライザーの信号処理パスの統合

---

## 🚀 セットアップ
```bash
# リポジトリのクローン
git clone [https://github.com/nununuma-sabu/music_player.git](https://github.com/nununuma-sabu/music_player.git)
cd music_player

# 依存ライブラリのインストール
pip install -r requirements.txt

# アプリケーションの起動
python main.py
```

## ビルドガイド
PyInstaller を使用して、アイコンやSVGアセットを含んだスタンドアロンの実行ファイルを生成可能です。
```PowerShell
pyinstaller --onefile --windowed `
            --name "PortfolioMusicPlayer" `
            --icon="styles/icons/app_icon.ico" `
            --add-data "styles/icons;styles/icons" `
            --collect-submodules core `
            --collect-submodules ui `
            --noconfirm `
            main.py
```