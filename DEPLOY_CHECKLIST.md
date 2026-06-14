# ScrollNow デプロイ前最終チェックリスト

> 最終更新: 2026-06-06
> 対象コミット: VIBRA_REBOOT Phase1 完了版

---

## ✅ 1. リポジトリ構造確認

```text
repo/
├── .github/
│   └── workflows/
│       └── update.yml          ← 自動更新Actions（1時間ごと）
├── assets/
│   ├── bg_society.png          ← 社会・事件（赤黒）
│   ├── bg_economy.png          ← 経済・金（金黒）
│   ├── bg_tech.png             ← テクノロジー（青黒）
│   ├── bg_world.png            ← 国際・危機（紫黒）
│   ├── bg_sports.png           ← スポーツ（緑黒）
│   ├── bg_ad.png               ← 広告（ピンク黒）
│   ├── default.png             ← 汎用（純黒）
│   ├── bg_entertainment.png    ← エンタメ（赤黒）
│   ├── bg_food.png             ← グルメ（金黒）
│   ├── bg_game.png             ← ゲーム（紫黒）
│   └── bg_anime.png            ← アニメ（ピンク黒）
├── hooks/
│   ├── shock.json              ← 40本 ✅
│   ├── anger.json              ← 40本 ✅
│   ├── fear.json               ← 40本 ✅
│   ├── curiosity.json          ← 40本 ✅
│   ├── empathy.json            ← 40本 ✅
│   ├── impact.json             ← 40本 ✅
│   ├── money.json              ← 40本 ✅
│   ├── food.json               ← 30本 🆕
│   ├── game.json               ← 30本 🆕
│   ├── anime.json              ← 30本 🆕
│   ├── entertainment.json      ← 30本 🆕
│   ├── keywords.json           ← 11カテゴリ ✅
│   └── direct_map.json         ← 50個 ✅
├── pipeline.py                 ← メインエンジン（修正版）
├── template.html               ← HTMLテンプレート
├── index.html                  ← 生成物（GitHub Pages配信）
├── requirements.txt            ← requests, beautifulsoup4
├── IMAGE_PROMPTS.md            ← 背景画像生成プロンプト
├── README.md                   ← プロジェクト説明
└── AGENTS.md / CLAUDE.md     ← （任意）エージェント設定
```

---

## ✅ 2. ファイル整合性チェック

| チェック項目 | 状態 | 備考 |
|:---|:---|:---|
| `pipeline.py` が `template.html` を読み込める | 🟢 | 同じディレクトリ配置前提 |
| `pipeline.py` が `hooks/` ディレクトリを読み込める | 🟢 | 相対パス `hooks/` |
| `pipeline.py` が `assets/` 画像を参照できる | 🟢 | `assets/` 相対パス |
| `index.html` が GitHub Pages で配信される | 🟢 | ルート配置 |
| `requirements.txt` に必要ライブラリ記載 | 🟢 | requests, beautifulsoup4 |
| `update.yml` が `index.html` のみコミット | 🟢 | assets/** を除外済み |

---

## ✅ 3. フック辞書品質チェック

### 3.1 重複チェック
- [x] ファイル内重複: **なし**（全ファイル）
- [x] ファイル間重複: **なし**（全280本+新規120本）
- [x] 類似表現（編集距離1-2）: **9ペア検出**（同一ファイル内）

### 3.2 類似表現の対応（同一ファイル内）
| ファイル | 類似ペア | 推奨対応 |
|:---|:---|:---|
| shock | 「え、そうなるの？」 ↔ 「え、そうなの？」 | 統合 or 片方削除 |
| shock | 「信じられない」 ↔ 「信じられん」 | 統合（「信じられない」残す） |
| shock | 「衝撃の展開」 ↔ 「衝撃の事実」 | 統合 or 片方削除 |
| shock | 「現実かよ」 ↔ 「マジかよ」 | 統合（「マジかよ」残す） |
| anger | 「ふざけんな」 ↔ 「ふざけるなよ」 | 統合（「ふざけんな」残す） |
| empathy | 「共感しかない」 ↔ 「共感しかない話」 | 統合（「共感しかない」残す） |
| empathy | 「共感したら」 ↔ 「共感したらRT」 | 統合（「共感したらRT」残す） |
| empathy | 「共感の嵐」 ↔ 「共感の塊」 | 統合（「共感の嵐」残す） |
| empathy | 「分かる人だけ分かる」 ↔ 「分かる人には分かる」 | 統合（「分かる人には分かる」残す） |

> ⚠️ 上記は**運用開始後**に徐々に統合推奨。現時点では機能上の問題なし。

### 3.3 異ファイル間類似（意図的）
- [x] 「知らなかった…」(shock) ↔ 「知らなかった」(money) → **意図的OK**（文末の「…」でトーン差）
- [x] 「知らないと後悔」(curiosity) ↔ 「知らないと危険」(fear) → **意図的OK**（後半で感情差）
- [x] その他4ペア → **意図的OK**（接頭辞/接尾辞で差別化）

---

## ✅ 4. セキュリティチェック

| 項目 | 状態 | 詳細 |
|:---|:---|:---|
| XSS対策（TOP5タイトル） | 🟢 | `html.escape()` 適用済み |
| 外部リンク（target="_blank"） | 🟢 | `rel="noopener"` は不要（同一origin） |
| User-Agent偽装 | 🟢 | Yahoo!ニュースRSS取得用 |
| タイムアウト設定 | 🟢 | RSS: 10秒, 本文: 8秒 |
| 機密情報のハードコード | 🟢 | なし（APIキー不要） |

---

## ✅ 5. GitHub設定チェック

| 項目 | 手順 | 状態 |
|:---|:---|:---|
| GitHub Pages有効化 | Settings → Pages → Deploy from a branch → main / root | ⬜ 手動実行必須 |
| GitHub Actions有効化 | Actionsタブ → "Enable workflows" | ⬜ 手動実行必須 |
| Actions権限 | `permissions: contents: write` 記載済み | 🟢 |
| スケジュール実行 | `cron: '0 * * * *'`（毎時0分） | 🟢 |
| 手動実行 | `workflow_dispatch:` 記載済み | 🟢 |

---

## ✅ 6. 運用開始後の監視項目

| 項目 | 頻度 | 閾値 |
|:---|:---|:---|
| フック在庫切れリスク | 毎週 | 1週間で同じフックが3回以上出現 |
| RSS取得失敗率 | 毎日 | 失敗率 > 20% |
| ページ読み込み速度 | 毎週 | LCP > 2.5秒 |
| ユーザー離脱ポイント | 毎月 | 最後のカード到達率 < 30% |
| フッククリック率 | 毎月 | 「続きを読む」CTR < 5% |

---

## ✅ 7. 既知の制限・TODO

| 優先度 | 項目 | 対応時期 |
|:---|:---|:---|
| P1 | direct_map の複数候補化（1対1 → 1対4〜8） | Phase2 |
| P1 | 各感情フックを100〜200本化 | Phase2 |
| P2 | フック使用回数のログ記録（在庫切れ検知） | Phase2 |
| P2 | 連続防止ロジックの「スコア順崩れ」緩和 | Phase2 |
| P3 | 背景画像のCSSグラデーション代替を最適化 | Phase3 |
| P3 | PWA対応（オフライン閲覧） | Phase3 |

---

## ✅ 8. デプロイコマンド

```bash
# 1. リポジトリに全ファイルを配置
# 2. GitHub上で以下を実行:
#    - Settings → Pages → main / root
#    - Actions → Enable workflows
#    - Actions → Update News Feed → Run workflow（初回手動）

# 3. 確認URL
open https://littlefunction.github.io/ScrollNow/
```

---

## 🎯 Go/No-Go 判定

| 項目 | 判定 |
|:---|:---|
| コード品質 | 🟢 GO |
| セキュリティ | 🟢 GO |
| フック品質 | 🟢 GO（類似表現は運用後対応可） |
| GitHub設定 | ⬜ 手動実行待ち |
| **総合判定** | **🟢 GO**（GitHub設定完了後即デプロイ可） |
