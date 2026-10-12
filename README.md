# RoboCon2026
2026年ロボコン用リポジトリ

## PiDog 強化学習シミュレーション環境 (pidog-rl)

犬型ロボット **PiDog**（SunFounder製）を MuJoCo 上の簡易四足モデルとして再現し、
Gymnasium のカスタム環境として強化学習（PPO, PyTorchバックエンド）を行うための
プロジェクト雛形です。

### 技術スタック

| 項目 | 採用技術 |
|---|---|
| 言語 | Python 3.11 |
| シミュレータ | [MuJoCo](https://mujoco.readthedocs.io/) |
| RL環境インターフェース | [Gymnasium](https://gymnasium.farama.org/) |
| 機械学習フレームワーク | PyTorch（[Stable-Baselines3](https://stable-baselines3.readthedocs.io/) のPPO経由） |
| 可視化 | `mujoco.viewer`（MuJoCo Viewer） |
| 開発環境 | VSCode, Git |
| パッケージ管理 | [uv](https://docs.astral.sh/uv/) |
| OS | Windows |

### セットアップ手順

1. **uv のインストール**（未インストールの場合）

   ```powershell
   powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   インストール後、`C:\Users\<user>\.local\bin` にPATHを通してください
   （新しいターミナルを開けば自動的に反映されます）。

2. **Python のセットアップ**（uvが自動管理するため個別インストール不要）

   ```powershell
   uv python install 3.11
   ```

3. **リポジトリを取得し、依存関係を同期**

   ```powershell
   git clone <このリポジトリのURL>
   cd RoboCon2026
   uv sync
   ```

   `uv sync` は `.venv` を作成し、`pyproject.toml` に記載された
   `mujoco` / `gymnasium` / `torch` / `stable-baselines3` などを自動インストールします。

4. **VSCode で開く**

   ```powershell
   code .
   ```

   `.vscode/extensions.json` に記載の拡張機能（Python, Pylance, Ruff）の
   インストールを促されたら導入してください。インタプリタは
   `.venv\Scripts\python.exe` が自動選択されます。

### 使い方

```powershell
# モデルをMuJoCo Viewerで可視化（関節が正しく動くか確認）
uv run scripts/view_model.py
uv run scripts/view_model.py --action-sweep   # 全アクチュエータを正弦波で動かして確認

# PPOで学習（PyTorchバックエンド、学習ログはTensorBoardで確認可能）
uv run scripts/train_ppo.py --timesteps 2000000
uv run tensorboard --logdir runs

# 学習済みモデルをビューアで再生
uv run scripts/play.py --model models/pidog_ppo.zip
```

### プロジェクト構成

```
src/pidog_rl/
  assets/pidog.xml      # PiDogを模した簡易四足モデル（MJCF）: 胴体+脚4本×2関節(肩/膝)
  envs/pidog_env.py      # Gymnasiumカスタム環境 "Pidog-v0"（前進速度＋姿勢維持を報酬化）
scripts/
  view_model.py          # MuJoCo Viewerでのモデル確認
  train_ppo.py            # Stable-Baselines3 PPO（PyTorch）での学習
  play.py                  # 学習済みポリシーの再生
```

`src/pidog_rl/assets/pidog.xml` の寸法・関節可動域は実機PiDogを参考にした概算値です。
実機によりフィットさせたい場合は、関節角度範囲やリンク長を実測値に合わせて調整してください。
より忠実なメッシュベースのモデルが必要な場合は
[Joel-Baptista/pidog_rl](https://github.com/Joel-Baptista/pidog_rl) が参考になります。

### 既知の注意点（日本語パス環境）

このリポジトリは `ロボコン\2026年度` のように非ASCII文字を含むパス上に配置されることを想定しています。
MuJoCoの一部のネイティブファイル読み込みAPI（`from_xml_path`）はWindowsでこのようなパスを正しく
開けない場合があるため、`PidogEnv`や`view_model.py`ではXMLファイルをPython側でテキストとして読み込み、
`mujoco.MjModel.from_xml_string()` でモデルを構築しています。同様の理由で `uv` のeditable install
(`.pth`)が正しく機能しない場合に備え、各スクリプト冒頭で `src` を `sys.path` に明示的に追加しています。
