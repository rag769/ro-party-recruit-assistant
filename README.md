# ro-party-recruit-assistant
 RO PT募集アシスタントBOT

## 概要
Discordのイベント機能を使ったROのPT募集をちょっと手助けするBOT

## 特徴
* Discordのイベントに疑似的に人数制限を設定可能
  * キャンセル待ち機能付き
* イベントリマインダー (開始30分前くらいにメンション通知)

## 必要なもの
* Python 3.8 以上
  * 必要パッケージは requirements.txt

## 使い方 (BOTプログラム)

### Discord側のBOT設定

OAuth2 の Bot Permissions は下記をチェックしてください
* General Permissions
  * Read Messages/View Channels
  * Manage Events
* Text Permissions
  * Send Messages

Botの Privileged Gateway Intents は全てチェックしてください
* Presence Intent
* Server Members Intent
* Message Content Intent

### BOTプログラム

1. config.py の変更
   * DISCORD_TOKEN
   * announce_channel (dict形式)
2. 必要ライブラリを取得  
   ```pip install -r requirements.txt```
3. プログラムを起動  
   ```python bot.py```


## 使い方 (Discord)
#### - BOTが動作していない時に作成・変更・ポチされたイベントの取込
イベントにポチした人の順番をdiscordは管理していないのでBOTが覚えています。  
BOTが動いていない時 (導入前とかクラッシュして落ちてたとか) に作成・変更・ポチされた  
イベントの情報が無いので下記コマンドで取り込んで下さい。

```?load イベントID```

__注意__  
>ポチ順は保証されません。キャンセル待ちになる人は多分正しく無いので、  
>募集人数を超えてるイベントは諦めてください...


#### - 参加確定した人の確認
キャンセル待ちが多い場合、discordのイベントGUIからは参加確定した人が確認し難いと思います。  
下記コマンドを使えば、参加確定した人・キャンセル待ちの人を別けて表示します

```?show イベントID```


## 免責および注意事
* 本BOTの使用により損害が発生したとしても一切の責任を負いません。
* 本BOTの仕様は予告なしに変更する事があります。
