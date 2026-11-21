# PiDog control

実機 PiDog（SunFounder製）向けのポーリング式センサー監視と出力インターフェースです。
強化学習でシミュレーション学習を行うコードは [pidog_rl/](../pidog_rl) に分離しています。

## 構成

- `main.py`: PiDogの初期化、センサー登録、ポーリング開始と終了処理
- `polling.py`: 登録されたセンサーを定期読み取りし、読み取り結果をスナップショットとして渡す機構
- `sensor/`: 距離、タッチ、IMU、音方向の入力アダプター
- `servo/`: 脚、頭、尾の出力アダプター

センサーアダプターは読み取りだけを担当し、動作判断やサーボ指令は行いません。
`PollingLoop`のスナップショット処理を後にイベントキューから呼び出す構成に替えられるよう、
入力の取得と判断処理を分離しています。現状の起動例はセンサー値を表示するだけで、機体を動かしません。
カメラIFは現時点では実装していません。カメラは`Pidog`本体のセンサーAPIではなく、
別ライブラリの`vilib`で起動・終了や検出設定を管理するためです。また、画像フレームを返すのか、
顔や色などの検出結果を返すのかは用途によって異なります。利用する機能と返却データを決めてから
入力IFを設計するための範囲上の判断であり、カメラ対応ができないという意味ではありません。
IMU値はSunFounderライブラリの`accData`と`gyroData`をそのまま返し、校正や単位変換は行いません。
音方向は未検知時に`-1`を返します。

## 開発環境とテスト（実機不要）

このプロジェクトはuvでPython 3.11を管理します。`pidog`ディレクトリで一度だけ環境を同期します。

```powershell
uv python install 3.11
uv sync
```

ハードウェア依存パッケージは開発環境に入れず、センサーやポーリング制御はモックを使ってテストします。

```powershell
uv run python -m unittest discover -s . -p "test_*.py"
```

## 実機での実行

SunFounderの`pidog`ライブラリとそのハードウェア依存関係をセットアップしたRaspberry Pi上で、
このディレクトリに移動して実行します。

```bash
sudo python3 main.py
```

ローカルのディレクトリ名とSunFounderライブラリのPythonパッケージ名がどちらも`pidog`のため、
このディレクトリはPythonパッケージ化せず、`main.py`を直接起動する構成にしています。
実機実行時は、SunFounderの`pidog`とGPIO/I2C等の依存関係を利用できるPython環境を使ってください。

## 出力IFの使用例

動作ロジックからサーボを直接操作する代わりに、個別の出力アダプターを使います。

```python
from servo import HeadServo, LegsServo, TailServo

head = HeadServo(dog)
legs = LegsServo(dog)
tail = TailServo(dog)

head.move(yaw=0, roll=0, pitch=0, speed=50)
tail.move([0], speed=50)
```

`LegsServo.move()`には8個の角度からなるフレーム列を渡します。
複数部位にまたがる名前付き動作は、個別のサーボIFではなく行動層から呼び出します。

## テスト

ハードウェアなしでポーリング制御を確認できます。

```bash
python3 -B -m unittest discover -s . -p "test_*.py"
```
