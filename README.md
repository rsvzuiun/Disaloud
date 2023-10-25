# Disaloud
Discordのテキストチャンネルを棒読みちゃんで読み上げてボイスチャンネルに垂れ流す

## インストール

### 仮想サウンドデバイス
ほかのものでも動くだろうけど。
https://vb-audio.com/Cable/

### 棒読みちゃん
動作テストは Ver0.11.0 b21 で行っています。
https://chi.usamimi.info/Program/Application/BouyomiChan/#Download
#### 棒読みちゃんの設定
* システム > アプリケーション連携 > 03)HTTP連携
  * 01)ローカルHTTPサーバ機能を使う: `True`
  * 02)ポート番号: 任意の番号、ただし `config.toml` とあわせる
* システム > SAPI / Speech Platform > 01)SAPI5
  * 01)SAPI5の音声合成エンジンを利用する: VOICEVOXを使う場合は `True`、使わない場合は不問
* システム > 音声出力デバイス
  * インストールした仮想サウンドデバイスを選択する、ただし `config.toml` とあわせる
* 他の設定はすきにしていいよ

### (Optional) VOICEVOX
棒読みちゃんと連携するため SAPIForVOICEVOX が必要、32bit版で登録してください。
https://voicevox.hiroshiba.jp/
https://github.com/shigobu/SAPIForVOICEVOX

### これ
```pwsh
python -m venv .venv
.venv\Scripts\activate
pip install .
```

`config.toml` にDiscord BOTのトークンを書き込む

## 実行方法
```pwsh
.venv\Scripts\activate
python -m disaloud
```
または `run.bat`
