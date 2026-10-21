# PiDogでできること：公式サンプル台帳

作成日：2026-10-16。対象コードは[取得情報](../pidog-sample/UPSTREAM.md)のコミットに固定。
全項目、公式説明とコードの静的確認に基づく。実機動作の確認結果は含まない。
公式Webは更新されるため、実装の判断は同梱コードと照合する。

## 公式の動作デモ

コード列はpidog-sample/examples/へのリンク。基本前提は組立・校正済みPiDog、Raspberry Pi、robot-hat等の公式実行環境。

| 能力・用途 | コードと入口 | 公式紹介 | 条件・流用時の注意 |
|---|---|---|---|
| 起床の連続演出 | [1_wake_up.py](../pidog-sample/examples/1_wake_up.py) / wake_up | [Wake Up](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_1_wakeup.html) | 伸び、体ひねり、座り、尾振り、pantを順次実行。動作待機も流用候補 |
| 基本動作・効果音の選択 | [2_function_demonstration.py](../pidog-sample/examples/2_function_demonstration.py) / actions、do_function | [Function Demonstration](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_2_function_demonstration.html) | 立つ、座る、伏せ、前後進、左右旋回、trot、居眠り、伸び、腕立て、首振り・傾け、尾振り。移動前の立位や腕立て後の遷移も確認する |
| 前進と近接物への停止・吠え | [3_patrol.py](../pidog-sample/examples/3_patrol.py) / patrol | [Patrol](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_3_patrol.html) | 超音波距離を使用。設定は15cm未満で反応。地図作成・経路計画・障害物を迂回する実装ではない |
| 接近やタッチへの反応 | [4_response.py](../pidog-sample/examples/4_response.py) / alert、head_nod、lean_forward | [Response](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_4_response.html) | 距離で後退・吠え、タッチで頭・尾・LEDを動かす。入力と演出の組み合わせの例 |
| 休息から音で起きる | [5_rest.py](../pidog-sample/examples/5_rest.py) / rest、is_sound | [Rest](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_5_rest.html) | 音検知で起きて見回す。発話内容の理解や話者識別はしない |
| 持ち上げ・下降の反応 | [6_be_picked_up.py](../pidog-sample/examples/6_be_picked_up.py) / be_picked_up、fly | [Be Picked Up](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_6_be_picked_up.html) | 加速度の閾値とフラグで判定。flyは持ち上げ時の脚のポーズ。閾値・軸方向は実機で確認 |
| 顔を頭で追う | [7_face_track.py](../pidog-sample/examples/7_face_track.py) / face_track | [Face Track](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_7_face_track.html) | カメラとvilibの顔検出を使用。人物ID識別や歩いて人物を追従する保証はない |
| 腕立ての演出 | [8_pushup.py](../pidog-sample/examples/8_pushup.py) / main、preset_actions.push_up | [Push Up](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_8_pushup.html) | 決められた姿勢変化による演出。実装はpush_upの動作定義を参照 |
| 遠吠えの演出 | [9_howling.py](../pidog-sample/examples/9_howling.py) / main、preset_actions.howling | [Howling](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_9_howling.html) | 姿勢、頭、効果音等の連続動作 |
| 姿勢補正と歩行・高さ操作 | [10_balance.py](../pidog-sample/examples/10_balance.py) / move_thread、main | [Balance](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_10_balance.html) | set_rpy(pid=True)、set_pose、足先座標から角度計算。IMU・機構校正が必要。任意の外乱で転倒しない保証ではない |
| キーボードで動作選択 | [11_keyboard_control.py](../pidog-sample/examples/11_keyboard_control.py) / OPERATIONS、run_operation | [Keyboard](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_11_keyboard_control.html) | curses等の端末環境。移動・姿勢・複合動作を操作に割り当てる参考 |
| スマホから操作・カメラ表示 | [12_app_control.py](../pidog-sample/examples/12_app_control.py) / main、run_command | [APP](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_12_app_control.html) | SunFounder Controller、sunfounder_controller、vilib、同一WLAN等が必要 |
| 色付きボールへの接近・旋回 | [13_ball_track.py](../pidog-sample/examples/13_ball_track.py) / ball_track | [Ball Track](https://docs.sunfounder.com/projects/pidog/en/latest/python/py_13_ball_track.html) | vilib.color_detectで赤色を指定。画像の中心・幅で頭と移動を制御。任意物体認識や距離の実測ではない |

## 再利用できる基本機能

[公式Easy Codingの入口](https://docs.sunfounder.com/projects/pidog/en/latest/python/play_with_python.html)と、同梱basic_examplesを参照。

| 部品 | 同梱コード（pidog-sample/からの相対パス） | 確認する点 |
|---|---|---|
| 初期化・終了 | basic_examples/1_pidog_init.py | 初期角、Pidog.closeによる終了 |
| 脚・頭・尾の制御 | basic_examples/2_legs_control.py、3_head_control.py、4_tail_control.py | 座標系、角度列、速度指定、同時実行とキュー |
| 停止・待機 | basic_examples/5_stop_actions.py、pidog/pidog.py | 各部位の停止範囲、wait_all_done等。停止命令と物理的な即時停止は区別 |
| 名前付き動作 | basic_examples/6_do_preset_actions.py、pidog/actions_dictionary.py | do_actionに渡す正式名と対象部位、前後の姿勢 |
| 複合的なしぐさ | pidog/preset_actions.py | hand_shake、high_five、scratch、nod、bark等。関数の実装と必要姿勢を個別に確認 |
| 音・LED | basic_examples/7_sound_effect.py、9_rgb_control.py、sounds/ | 録音効果音と音声合成を区別 |
| 超音波距離 | basic_examples/8_ultrasonic_read.py | 単位、無効値、対象物や向きによる検出条件 |
| IMU | basic_examples/10_imu_read.py、examples/imu_calibration.py | 軸・単位・校正・機体取付方向 |
| 音方向・タッチ | basic_examples/11_sound_direction_read.py、12_dual_touch_read.py | イベントや入力値の定義。音声理解とは別 |
| カメラ | basic_examples/13_camera_easy_use.py | vilibとカメラ環境 |

追加の音声対話候補としてexamples/voice_active_dog.py、19_voice_active_dog_ollama.py、20_voice_active_dog_gpt.py等が存在する。上の13デモの紹介との対応確認は未実施。採用時はSTT/TTS、モデル、外部サービス、認証情報、通信、遅延の条件を別途調べる。

## 台帳の使い方

相談内容に関連する項目から公式コードを読み、流用できる処理と変更が必要な部分を確認する。
台帳は公式サンプルを探す索引であり、機体の性能保証や網羅的な能力評価ではない。
実機の性能や動作結果が必要な場合は、利用する機体・環境で別途確認する。

## Webとコードの差

公式ページの掲載コードに旧import（from preset_actions等）が残る場合がある。同梱版はfrom pidog.preset_actionsを使う箇所があるため、そのままWebの断片をコピーせず確認する。
デモ紹介中のpushupという表記に対して、同梱コードのアクション名はpush_up。正確な呼び出し名はコードを採用する。
