# ScrollNow Phase2.5 デプロイ手順書

> 対象: VIBRA_REBOOT Phase2.5 完全実装版（広告機能含む）
> 最終更新: 2026-06-07
> 想定時間: 20〜30分（初回）

---

## Step 0: 事前準備

### 必要なもの
- GitHubアカウント（`littlefunction` でログイン済みのこと）
- リポジトリ `littlefunction/ScrollNow`（空のままでOK）
- このZIPファイルの中身（24ファイル）
- **楽天アフィリエイトID**（`af.xxxxxxxx` 形式）
- **楽天アプリケーションID**（`000000000000000000` 形式）

> ⚠️ 楽天アフィリエイトID・アプリケーションIDがない場合は、
> [楽天ウェブサービス](https://webservice.rakuten.co.jp/) で取得してください。
> 取得までに数日かかる場合があります。

### ZIPファイルの中身確認
```
ScrollNow_Phase2.5_Complete.zip
├── .github/workflows/
│   ├── update.yml          # 毎時更新Actions
│   └── cleanup.yml         # 毎日クリーンアップActions
├── article/                # （空ディレクトリ。初回は手動作成）
├── assets/                 # （空ディレクトリ。背景画像は後で配置）
├── hooks/
│   ├── shock.json          # 40本
│   ├── anger.json          # 40本
│   ├── curiosity.json      # 40本
│   ├── empathy.json        # 40本
│   ├── fear.json           # 40本
│   ├── impact.json         # 40本
│   ├── money.json          # 40本
│   ├── food.json           # 30本
│   ├── game.json           # 30本
│   ├── anime.json          # 30本
│   ├── entertainment.json  # 30本
│   ├── keywords.json       # 11カテゴリ
│   └── direct_map.json     # 50個
├── pipeline.py             # Phase2.5完全実装版（広告機能含む）
├── template.html           # フィードテンプレート
├── template_article.html   # 個別記事テンプレート
├── requirements.txt        # requests, beautifulsoup4
├── robots.txt              # クロール制御
├── IMAGE_PROMPTS.md        # 背景画像生成プロンプト
├── README.md               # プロジェクト説明
├── DEPLOY_CHECKLIST.md     # デプロイ前チェックリスト
└── DEPLOY_GUIDE.md         # このファイル
```

> ⚠️ `index.html` と `sitemap.xml` は pipeline.py 実行時に自動生成されるため、ZIPには含めていません。

---

## Step 1: リポジトリにファイルを配置

### 1.1 ローカルにクローン

```bash
git clone https://github.com/littlefunction/ScrollNow.git
cd ScrollNow
```

### 1.2 ZIPの中身を全てコピー

```bash
# ZIPを展開したディレクトリから全ファイルをコピー
cp -r /path/to/unzipped/* ./
```

### 1.3 空ディレクトリを作成

```bash
mkdir -p article
mkdir -p assets
```

### 1.4 確認

```bash
ls -la
# 期待される出力:
# .github/  article/  assets/  hooks/  pipeline.py  template.html
# template_article.html  requirements.txt  robots.txt  IMAGE_PROMPTS.md  README.md
```

---

## Step 2: GitHub Secrets に楽天IDを登録（⚠️ 必須）

### 2.1 Secrets設定ページを開く

```
https://github.com/littlefunction/ScrollNow/settings/secrets/actions
```

### 2.2 「New repository secret」ボタンをクリック

### 2.3 2つのSecretを登録

#### Secret 1: RAKUTEN_AFFILIATE_ID

| 項目 | 値 |
|:---|:---|
| Name | `RAKUTEN_AFFILIATE_ID` |
| Secret | `af.xxxxxxxx`（あなたの楽天アフィリエイトID） |

#### Secret 2: RAKUTEN_APP_ID

| 項目 | 値 |
|:---|:---|
| Name | `RAKUTEN_APP_ID` |
| Secret | `000000000000000000`（あなたの楽天アプリケーションID） |

### 2.4 登録確認

Secrets一覧に以下が表示されていることを確認：

```
✓ RAKUTEN_AFFILIATE_ID
✓ RAKUTEN_APP_ID
```

> ⚠️ **重要**: これらのIDはハードコードせず、必ずSecretsに格納してください。
> pipeline.py は実行時に `os.environ.get()` でこれらを読み込みます。
> IDが未設定の場合、広告URLは検索URLのみ（アフィリエイト付与なし）で生成されます。

---

## Step 3: GitHub Pages 有効化

### 3.1 リポジトリの Settings を開く

```
https://github.com/littlefunction/ScrollNow/settings/pages
```

### 3.2 Source を設定

| 項目 | 設定値 |
|:---|:---|
| Source | `Deploy from a branch` |
| Branch | `main` |
| Folder | `/ (root)` |

### 3.3 Save をクリック

> 📝 初回は数分かかる場合があります。

---

## Step 4: GitHub Actions 有効化

### 4.1 Actions タブを開く

```
https://github.com/littlefunction/ScrollNow/actions
```

### 4.2 "I understand my workflows, go ahead and enable them" をクリック

> 初回のみ。ワークフローファイル（`.github/workflows/*.yml`）が認識される。

### 4.3 ワークフロー確認

以下の2つが表示されることを確認：

| ワークフロー名 | 実行頻度 | 内容 |
|:---|:---|:---|
| `Update News Feed` | 毎時0分 + 手動 | pipeline.py実行 → index.html + article/*.html + sitemap.xml生成 |
| `Cleanup Old Articles` | 毎日午前3時 + 手動 | 90日超過のarticle/*.htmlを削除 |

---

## Step 5: 初回手動実行

### 5.1 Update News Feed を手動実行

```
https://github.com/littlefunction/ScrollNow/actions/workflows/update.yml
```

「Run workflow」→「Run workflow」をクリック。

### 5.2 実行結果を確認（1〜2分）

| ステップ | 期待される出力 |
|:---|:---|
| Checkout code | ✅ |
| Set up Python | ✅ |
| Install dependencies | ✅ |
| Run pipeline | `[1/5] フックエンジン初期化中...` → `✅ index.html + article pages generated successfully.` |
| Commit and Push | `Update news feed [skip ci]` |

### 5.3 エラーが出た場合

```bash
# ローカルで動作確認
cd ScrollNow
pip install -r requirements.txt
python pipeline.py
```

主な原因：
- `hooks/` ディレクトリがない → `mkdir hooks`
- `article/` ディレクトリがない → `mkdir article`
- `template.html` または `template_article.html` が存在しない → ファイル配置ミス
- **Secrets未設定** → Step 2に戻る（未設定でも動作しますが、広告URLにアフィリエイトIDが付きません）

---

## Step 6: デプロイ確認

### 6.1 GitHub Pages URL にアクセス

```
https://littlefunction.github.io/ScrollNow/
```

### 6.2 確認項目

| 項目 | 確認方法 |
|:---|:---|
| フィードが表示される | 画面にカードが1枚表示される |
| スワイプ動作 | マウスホイール / キーボード↑↓ / スマホスワイプ |
| ジャンルバナー | 各カード上部に色付きバナー |
| フック表示 | カード中央に大きな文字 |
| サマリー表示 | フック下に小さめの文字 |
| キャッチコピー | 右下に縦書き金色文字 |
| プログレスドット | 下部に点が表示される |
| TOP5カード | 最後のカードに「🔥 今日の重要ニュース」 |
| **広告カード** | **3件ごとにPRバナーのカードが表示される** |
| **広告CTA** | **「人気商品を見る →」がテキストリンク風** |
| **次の記事予告** | **広告カード下部に「次：「大谷翔平が…」」** |

### 6.3 個別記事ページの確認

```
https://littlefunction.github.io/ScrollNow/article/
```

ファイル一覧が表示されればOK。個別ページURL例：
```
https://littlefunction.github.io/ScrollNow/article/20260607-000000-tech-001.html
```

### 6.4 sitemap.xml の確認

```
https://littlefunction.github.io/ScrollNow/sitemap.xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://littlefunction.github.io/ScrollNow/</loc>
    <lastmod>2026-06-07T00:00:00+09:00</lastmod>
    <changefreq>hourly</changefreq>
    <priority>1.0</priority>
  </url>
  <!-- article/*.html のURLが追加される -->
</urlset>
```

### 6.5 robots.txt の確認

```
https://littlefunction.github.io/ScrollNow/robots.txt
```

```
User-agent: *
Allow: /
Sitemap: https://littlefunction.github.io/ScrollNow/sitemap.xml
```

---

## Step 7: 自動更新の確認（任意・翌日以降）

### 7.1 Actions 実行履歴を確認

```
https://github.com/littlefunction/ScrollNow/actions/workflows/update.yml
```

毎時0分に自動実行されていることを確認。

### 7.2 コミット履歴を確認

```
https://github.com/littlefunction/ScrollNow/commits/main
```

`Update news feed [skip ci]` のコミットが毎時間増えていることを確認。

---

## Step 8: 背景画像の配置（オプション・後回し可）

### 8.1 IMAGE_PROMPTS.md を参照して生成

```bash
# 例：Midjourney / DALL-E / Stable Diffusion で生成
cat IMAGE_PROMPTS.md
```

### 8.2 assets/ に配置

```bash
ScrollNow/assets/
├── bg_society.png      # 社会・事件（赤黒）
├── bg_economy.png      # 経済・金（金黒）
├── bg_tech.png         # テクノロジー（青黒）
├── bg_world.png        # 国際・危機（紫黒）
├── bg_sports.png       # スポーツ（緑黒）
├── bg_ad.png           # 広告（ピンク黒）
├── default.png         # 汎用（純黒）
├── bg_entertainment.png # エンタメ（赤黒）
├── bg_food.png         # グルメ（金黒）
├── bg_game.png         # ゲーム（紫黒）
└── bg_anime.png        # アニメ（ピンク黒）
```

### 8.3 画像がない場合

CSSグラデーションで自動代替される。即運用可能。

---

## Step 9: 広告機能の動作確認

### 9.1 広告カードの表示確認

フィードをスクロールし、3件ごとに表示される広告カードを確認：

```
┌────────────────┐
背景：bg_money.png

📢 PR

電気代高すぎない？

最近、
節約グッズを探す人が増えています。

人気商品を見る →

──────────

次：「大谷翔平が…」
└────────────────┘
```

### 9.2 アフィリエイトURLの確認

広告カードの「人気商品を見る →」をクリックし、URLに以下が含まれていることを確認：

```
https://search.rakuten.co.jp/search/mall/節電グッズ/?scid=af.xxxxxxxx&sitem=000000000000000000
```

> ⚠️ Secrets未設定の場合、`scid=` と `sitem=` が付きません。
> その場合は Step 2 に戻って Secrets を登録してください。

### 9.3 広告ローテーション確認

1週間経過後、同じ感情の記事に対して別のキーワードが表示されることを確認：

| 週 | 表示されるキーワード |
|:---|:---|
| 第1週 | 節電グッズ |
| 第2週 | 防災用品 |
| 第3週 | 収納グッズ |
| 第4週 | 節電グッズ（循環） |

---

## 運用開始後の監視

### 毎日確認すべき項目

| 確認項目 | URL |
|:---|:---|
| Actions実行状況 | `https://github.com/littlefunction/ScrollNow/actions` |
| サイト表示確認 | `https://littlefunction.github.io/ScrollNow/` |

### 毎週確認すべき項目

| 確認項目 | 閾値 | 対応 |
|:---|:---|:---|
| 同じフックの出現頻度 | 1週間で3回以上 | フック辞書拡充（各感情100〜200本化） |
| RSS取得失敗率 | > 20% | Yahoo!ニュースRSSの仕様変更確認 |
| ページ読み込み速度 | LCP > 2.5秒 | 画像最適化 or CSSグラデーション化 |
| 広告CTR | < 1% | フック・CTA文言の変更検討 |

### 毎月確認すべき項目

| 確認項目 | 閾値 | 対応 |
|:---|:---|:---|
| 最後のカード到達率 | < 30% | UX改善（カード数調整 or フック品質） |
| 「続きを読む」CTR | < 5% | フック品質 or 配置変更 |
| 個別ページのGoogleインデックス状況 | `site:littlefunction.github.io/ScrollNow/article/` | インデックスされていなければsitemap確認 |
| 広告収益（楽天レポート） | 推移確認 | キーワード・フックの効果測定 |

---

## トラブルシューティング

### Q1: pipeline.py 実行時に `ModuleNotFoundError`

```bash
pip install -r requirements.txt
```

### Q2: Actionsが失敗する

```bash
# ローカルで再現確認
cd ScrollNow
python pipeline.py
```

主な原因：
- `hooks/` ディレクトリが存在しない
- `article/` ディレクトリが存在しない
- `template.html` または `template_article.html` が存在しない
- Yahoo!ニュースRSSへのアクセス制限（User-Agent偽装で対応済み）

### Q3: サイトが表示されない

1. GitHub PagesのSource設定が `main / root` になっているか確認
2. `index.html` がリポジトリルートに存在するか確認
3. Actionsの実行履歴でエラーがないか確認

### Q4: スワイプが効かない

- PC: マウスホイール or キーボード↑↓
- スマホ: タッチスワイプ
- どちらも効かない場合はJavaScriptエラー。ブラウザのDevToolsで確認。

### Q5: article/ ディレクトリが404になる

初回実行時は記事が生成されていない可能性あり。1時間後の自動更新、または手動実行を待つ。

### Q6: 広告URLにアフィリエイトIDが付いていない

1. Step 2（Secrets登録）を確認
2. Secret名が正しいか確認：`RAKUTEN_AFFILIATE_ID` と `RAKUTEN_APP_ID`
3. Actionsの実行ログで環境変数が読み込まれているか確認

### Q7: 広告カードが表示されない

1. ニュース記事が10件取得できているか確認（件数不足の場合、広告挿入ロジックが動作しない）
2. pipeline.py の実行ログで `ad_inserted` の値を確認

---

## 付録: ファイル配置の最終確認

```bash
# リポジトリルートで実行
find . -type f | grep -v ".git" | sort
```

期待される出力：
```
./.github/workflows/cleanup.yml
./.github/workflows/update.yml
./DEPLOY_CHECKLIST.md
./DEPLOY_GUIDE.md
./HANDOVER.md
./IMAGE_PROMPTS.md
./PHASE2_ARTICLE_PAGES.md
./PHASE2_ARTICLE_PAGES_v2.md
./README.md
./cleanup.yml
./hooks/anger.json
./hooks/anime.json
./hooks/curiosity.json
./hooks/direct_map.json
./hooks/empathy.json
./hooks/entertainment.json
./hooks/fear.json
./hooks/food.json
./hooks/game.json
./hooks/impact.json
./hooks/keywords.json
./hooks/money.json
./hooks/shock.json
./pipeline.py
./requirements.txt
./robots.txt
./template.html
./template_article.html
```

> `index.html`, `sitemap.xml`, `article/*.html` は pipeline.py 実行後に生成されます。

---

## 完了！

🎉 ScrollNow Phase2.5 のデプロイが完了しました。

次の更新まで、自動で動作します。
