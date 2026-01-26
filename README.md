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
高レイヤ（UI）、ミドルレイヤ（Core/Logic）、低レイヤ（Engine）を明確に分離しています。

### 1. Python UI Layer
- **PySide6**: ダークモードを基調としたネイティブUI。各パーツをコンポーネント化。
- **SVG Icons**: OS環境に依存しない、スケーラブルなグラフィック表現。

### 2. Python Core Layer
- **Metadata Handler**: `mutagen` を用いたメタデータ抽出。MP3やFLACなどのマルチフォーマットに対応。
- **Logic Isolation**: UIからロジックを分離し、ユニットテストが可能な設計を採用。

### 3. Rust Layer (Backend - Under Development)
- **Performance**: SIMD等を意識した高速な信号処理ロジック。
- **Bridge**: PyO3によるPythonモジュールとしての統合。

---

## 📈 現在の実装状況
- [x] PySide6を用いたダークモードGUIの構築
- [x] 各種コンポーネント（Slider, Controls, DropZone）のモジュール化
- [x] ファイル選択ダイアログの実装（WSL2環境でのWindowsファイルアクセス対応）
- [x] Mutagenによるメタデータ抽出ロジックの実装（MP3/FLAC対応）
- [x] 信号処理ロジックの分離・リファクタリング
- [ ] プレイリスト表示機能の実装
- [ ] Rust製エンジンの統合
- [ ] リアルタイム・イコライザーの実装

## 🗓️ [2026-01-26] ユニットテストの導入とロジックのリファクタリング

* **関心の分離（Separation of Concerns）**
    * **改善**: `MainWindow` に記述されていたメタデータ抽出ロジックを `core/metadata.py` へ移譲。
    * **メリット**: UI層（表示）とデータ層（解析）を切り離すことで、UIを表示させずにロジックのみをテストすることが可能になりました。

* **pytest による単体テストの実装**
    * **モックの活用**: `unittest.mock` を使用し、実際の音声ファイルを用意することなく、MP3やFLACの解析ロジックを検証可能にしました。
    * **トラブルシューティング**: 
        * **インポートパスの問題**: `python3 -m pytest` を用いた実行により、プロジェクトルートを `sys.path` に追加し、モジュール解決エラーを回避。
        * **パッチ対象の適正化**: `mutagen.File` ではなく、実際にインポートされて使用されている `core.metadata.MutagenFile` をパッチ対象とすることで、モックを確実に機能させました。

* **テスト実行手順**
    ```bash
    # プロジェクトルートで実行
    python3 -m pytest
    ```

楽曲データを選択し、メタデータ取得までの流れ
![モック](music_player/docs/images/モック.png)
![楽曲データ選択](music_player/docs/images/楽曲データ選択.png)
![メタデータ(曲名等)](music_player/docs/images/メタデータ(曲名等).png)
---

## 🚀 セットアップ
```bash
# リポジトリのクローン
git clone https://github.com/nununuma-sabu/music_player.git
cd music_player

# 依存ライブラリのインストール
pip install -r requirements.txt

# アプリケーションの起動
python main.py
```

## 🐧 WSL2 / Linux 環境での実行について
本アプリは WSL2 (Ubuntu) 上での動作を確認していますが、Linux環境特有のフォントレンダリングや文字化け（豆腐現象）を回避するため、以下の設定を推奨します。

### 1. 日本語フォントのインストール
WSL側に日本語フォントがインストールされていない場合、UIの日本語が正しく表示されません。以下のコマンドで標準的なフォントをインストールしてください。

```bash
sudo apt update
sudo apt install -y fonts-noto-cjk fonts-ipafont-gothic
fc-cache -fv
```

### 2. 特殊記号（シンボル）の表示
再生・停止などのメディア操作記号は、環境に左右されないよう SVGベクター形式のアイコン を採用しています。これにより、特定のシンボルフォント（fonts-symbola等）が未導入の環境でも、デザインが崩れることなく一貫したUIを提供します。

