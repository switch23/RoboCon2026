# RoboCon2026
2026年ロボコン用リポジトリ

## ディレクトリ構成

| ディレクトリ | 内容 |
|---|---|
| [pidog/](./pidog) | 実機PiDogの通常開発用コード（制御プログラム、競技用ロジックなど） |
| [pidog_rl/](./pidog_rl) | PiDogをMuJoCo上でシミュレーションし、歩行を強化学習させるプロジェクト |
| [pidog_jump_rl/](./pidog_jump_rl) | 歩行用とは独立した、ジャンプと安定着地を強化学習させるプロジェクト |
| [pidog-sample/](pidog-sample/) | 公式コードの参照用コピー。[取得元・バージョン](pidog-sample/UPSTREAM.md)とLICENSEを保持 |
| [docs/pidog-capabilities.md](docs/pidog-capabilities.md) | 公式デモと対応コードの台帳 |
| [.agents/skills/pidog-official-examples/](.agents/skills/pidog-official-examples/) | 相談中に関連する公式デモを提案するスキル |

強化学習環境のセットアップ・使い方は、[歩行](./pidog_rl/README.md) と
[ジャンプ](./pidog_jump_rl/README.md) の各READMEを参照してください。
