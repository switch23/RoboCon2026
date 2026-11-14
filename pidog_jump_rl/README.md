# PiDog Jump RL

歩行用の [`pidog_rl`](../pidog_rl) とは独立した、MuJoCo上の簡易PiDogモデルで
ジャンプ方策を学習・評価するプロジェクトです。実機PiDogを直接制御するものではありません。

## セットアップ

Python 3.11以上と [uv](https://docs.astral.sh/uv/) が必要です。

```powershell
cd pidog_jump_rl
uv sync
```

## 学習

```powershell
uv run scripts/train_ppo.py --timesteps 2000000 --run-name pidog_jump_ppo_v6
```

既定では8環境を並列に使います。負荷が高い場合は `--n-envs 2` などに減らせます。
学習済みモデルは `models\pidog_jump_ppo_v6.zip`、TensorBoardログは `runs\` に保存されます。

```powershell
uv run tensorboard --logdir runs
```

## 評価・再生

評価は決定論的な方策で複数エピソードを実行し、胴体の最高上昇量、最高点での左右対称性と
脚関節の使用度、着地姿勢、4本の接地数、安定状態の継続ステップ数、終了理由、成功数を出力します。

```powershell
uv run scripts/evaluate.py --model models/pidog_jump_ppo_v6.zip --episodes 20
uv run scripts/play.py --model models/pidog_jump_ppo_v6.zip --episodes 3
```

成功は「リセット時の胴体高さから4 cm以上上昇し、着地後に4本の足が接地した
直立・低速度・低関節速度の状態を0.5秒連続で保つこと」と定義しています。出力する高さはMuJoCoモデルの
胴体中心の上昇量（m）です。高さだけでなく、安定着地と成功率も併せて確認してください。

## 環境と報酬

- 行動：8個の脚関節サーボ目標角度（方策出力は[-1, 1]、環境内で[-90°, 90°]に変換）
- 観測：関節位置・速度、胴体姿勢・速度、足の接地状態、ジャンプの進行状態
- 報酬：ジャンプの最高高さ・頂点の左右対称性・各脚の関節使用度、下降中の4本接地・姿勢・関節を立位に戻す動作、着地後の安定継続を評価。制御量と転倒にはペナルティ
- 1エピソード：1回の離陸後、安定着地・転倒・接地後の再跳躍・最大600環境ステップのいずれかで終了

モデルMJCFは `src\pidog_jump_rl\assets\pidog_jump.xml` に同梱しています。
歩行プロジェクトのモデルとは別ファイルなので、機体形状を変更するときは必要に応じて
両方を更新してください。公式サンプルの
[`6_be_picked_up.py`](../pidog-sample/examples/6_be_picked_up.py) にある `fly()` は、
持ち上げられた際の脚ポーズであり、ジャンプ学習や着地制御の実装ではありません。

この簡易モデルで学習した方策を実機PiDogへそのまま適用することはできません。
実機利用には、実機の物理特性・サーボ制御・センサーに合わせた別途の設計と安全検証が必要です。
