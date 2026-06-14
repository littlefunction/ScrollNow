【1. このチャットの目的】

- VIBRA_REBOOT（ScrollNow）プロジェクトの完全実装・デプロイ準備を行うこと
- ニュースアプリではなく「TikTokのようにスワイプするニュース消費体験」をGitHub Pagesで永久運用するシステムを構築すること
- 最終的なゴール：GitHub Pagesへのデプロイと、1時間ごとの自動更新（GitHub Actions）が動作する状態にすること

---

【2. 新しいチャットに切り替える理由】

- 会話が長くなり（20ターン以上）、コンテキストが複雑化した
- ファイル数が20ファイル以上に増え、添付・管理が煩雑になった
- Phase1（基本実装）→ Phase2（SEO/AIO対策・個別記事ページ生成）と段階を踏んで実装し、次はデプロイ実行や追加整備に移りたい
- 次のチャットでは「デプロイ手順の実行」や「AGENTS.md/CLAUDE.md/GEMINI.mdの作成」など、新しいテーマに集中しやすくしたい

---

【3. 背景・前提条件】

### プロジェクト概要
- **プロジェクト名**: VIBRA_REBOOT（公開名：ScrollNow）
- **設計思想**: 「ニュースアプリ」ではなく「話題のTikTok（脳死消費）」。情報量削減ではなく、供給量が少ない前提で情報密度を上げる方向性
- **運用形態**: GitHub Pages（完全無料・サーバーレス）+ GitHub Actions（1時間ごと自動更新）
- **ニュースソース**: Yahoo!ニュース RSS（APIキー不要・無料）
- **フック生成**: 外部JSON辞書 + キーワード判定（LLM不要・トークン不要）
- **感情分類**: shock/anger/fear/curiosity/empathy/impact/money/entertainment/food/game/anime（11カテゴリ）

### 技術スタック
- Python 3.10（BeautifulSoup + requests）
- 静的HTML（GitHub Pages配信）
- GitHub Actions（cron: '0 * * * *'）
- 背景画像：CSSグラデーション代替可能（画像がなくても動作）

### 重要な設計思想（変更不可）
1. **LLM禁止**: フック生成・要約・感情分類はすべてルールベース。LLMを使うとコスト・速度・依存性が増えるため
2. **UX保護**: フィード（index.html）から個別記事ページへの導線は設けない。スワイプ体験を壊さない
3. **供給量抑制**: 1回あたり10件程度。過剰供給より情報密度を重視
4. **Layer分離**: Layer1（ユーザー/TikTok体験）と Layer2（Google/SEO資産）を分離

### ファイル構成の前提
```
repo/
├── .github/workflows/
│   ├── update.yml          # 毎時更新（index.html + article/*.html + sitemap.xml）
│   └── cleanup.yml         # 毎日午前3時（90日超過記事削除）
├── article/                # 個別記事ページ（自動生成・90日保持）
├── assets/                 # 背景画像（手動配置・画像なしでもCSS代替で動作）
├── hooks/                  # フック辞書（400本）
│   ├── shock.json (40)
│   ├── anger.json (40)
│   ├── curiosity.json (40)
│   ├── empathy.json (40)
│   ├── fear.json (40)
│   ├── impact.json (40)
│   ├── money.json (40)
│   ├── food.json (30) 🆕
│   ├── game.json (30) 🆕
│   ├── anime.json (30) 🆕
│   ├── entertainment.json (30) 🆕
│   ├── keywords.json
│   └── direct_map.json (50個)
├── pipeline.py             # Phase2完全実装版
├── template.html           # フィードテンプレート（JSON-LD + メタタグ最適化）
├── template_article.html   # 個別記事テンプレート（NewsArticle JSON-LD + OGP）
├── index.html              # 生成物（GitHub Pagesで配信）
├── sitemap.xml             # 自動生成（index.html + article/*.html）
├── robots.txt              # 静的
├── requirements.txt        # requests, beautifulsoup4
├── IMAGE_PROMPTS.md        # 背景画像生成プロンプト（11種）
└── README.md
```

### デプロイ先
- GitHubリポジトリ: `https://github.com/littlefunction/ScrollNow`
- GitHub Pages URL: `https://littlefunction.github.io/ScrollNow/`

---

【4. ここまでの経緯】

### Phase0: プロジェクト共通ルールの確認
- AGENTS.md / CLAUDE.md / GEMINI.md / SKILL.md の分離設計を確認
- RTK Filtering Logic（コマンド出力の要約ルール）を確認

### Phase1: 基本実装レビュー
1. **5ファイルの受領**: IMAGE_PROMPTS.md, pipeline.py, README.md, requirements.txt, template.html
2. **9ファイルの受領**: フック辞書（shock, anger, curiosity, empathy, fear, impact, money, keywords, direct_map）
3. **1ファイルの受領**: GitHub Actions（update.yml）
4. **pipeline.pyレビュー**: 
   - 確認項目6つすべてPASS
   - build_cards関数のreturn文改行分割バグを発見・修正提案
   - HookEngineの不足ファイル（food/game/anime/entertainment.json）を検出

### Phase1.5: フック辞書拡充
- 不足ファイル4つを生成（food.json, game.json, anime.json, entertainment.json：30本ずつ）
- 既存7ファイルの重複チェック + 差分補充（各10本追加 → 40本化）
- 類似表現の検出（同一ファイル内9ペア、異ファイル間6ペア）
- 総フック数：400本（shock〜money: 40本×7 + food〜entertainment: 30本×4）

### Phase1.5: パッチ適用
- pipeline.py: 不足ファイル警告追加 + XSS防御（html.escape）
- update.yml: コミット対象をindex.htmlのみに（assets/**除外）

### Phase1.5: デプロイチェックリスト作成
- リポジトリ構造確認、ファイル整合性、フック品質、セキュリティ、GitHub設定、運用監視項目、既知の制限・TODOを文書化

### Phase2: SEO/AIO対策設計会議
- **SEO担当**: 記事個別ページ生成、カテゴリページ、sitemap.xmlを提案
- **AIO担当**: NewsArticle JSON-LD、FAQ構造を提案
- **TikTok体験担当**: 長文増加に反対（UX保護）
- **マーケ責任者**: 表面（フィード）と裏側（SEOテキスト）の分離を提案 → 隠しテキストは危険と判断
- **プロデューサー**: Layer分離（Layer1=ユーザー、Layer2=Google、Layer3=AI）を提案

### Phase2: 設計案v1 → フィードバック → v2修正
- **URL命名**: 日本語slug → 連番（`{genre}-{seq:03d}`）に修正（日本語slug崩壊回避）
- **保持期間**: 30日 → 90〜180日に修正（Googleインデックスサイクル考慮）
- **description**: 3行要約 → `hook + title` に修正（LLM導入の誘惑を断つ）
- **FAQPage**: 不採用（薄いページ大量発生リスク）
- **フィード→記事導線**: 不採用（UX保護）

### Phase2: 完全実装
- template_article.html: 個別記事ページテンプレート（ダークテーマ・レスポンシブ・NewsArticle JSON-LD + OGP/Twitter Card）
- pipeline.py: generate_article_pages() + cleanup_old_articles() + sitemap.xml個別ページURL追加
- update.yml: article/*.html をコミット対象に追加
- cleanup.yml: 毎日午前3時実行の90日クリーンアップActions

---

【5. 決定事項】

### 設計思想（変更不可）
1. **LLM禁止**: フック生成・要約・感情分類はすべてルールベース
2. **UX保護**: フィードから個別記事ページへの導線なし
3. **供給量抑制**: 1回あたり10件程度
4. **Layer分離**: Layer1（ユーザー）と Layer2（Google/AI）を分離

### 技術仕様（確定）
- URL: `/article/{YYYYMMDD}-{HHMMSS}-{genre}-{seq:03d}.html`
- 保持期間: 90日（cleanup.ymlで毎日午前3時実行）
- description: `hook + title`（AI要約禁止）
- sitemap.xml: 最大5000件（index.html priority=1.0, article priority=0.6）
- フック総数: 400本（11感情カテゴリ）
- direct_map: 50個（1対1、将来は複数候補化を検討）

### 不採用項目（確定）
- FAQPage
- フィード→記事導線
- AI要約（LLM）
- 隠しテキスト
- 5000文字記事
- 日本語slug

### ファイル配置（確定）
- `.github/workflows/update.yml`: 毎時更新
- `.github/workflows/cleanup.yml`: 毎日午前3時クリーンアップ
- `article/`: 個別記事ページ（自動生成）
- `assets/`: 背景画像（手動配置、なくても動作）
- `hooks/`: フック辞書（400本）

---

【6. 未解決事項・保留事項】

### デプロイ前に必要な作業
1. **GitHub設定（手動）**:
   - Settings → Pages → Source: `Deploy from a branch` → Branch: `main` / `root`
   - Actionsタブ → "Enable workflows"
   - Actions → Update News Feed → Run workflow（初回手動実行）

2. **背景画像の生成・配置（オプション）**:
   - IMAGE_PROMPTS.md を参照して11枚生成
   - なくてもCSSグラデーションで代替可能（即運用可能）

3. **リポジトリへのファイルプッシュ**:
   - 全20ファイルを `littlefunction/ScrollNow` にプッシュ

### 運用開始後の対応（Phase2+）
4. **フック在庫切れ監視**: 1週間で同じフックが3回以上出現したら拡充（各感情100〜200本化）
5. **direct_map複数候補化**: 1対1 → 1対4〜8（将来対応）
6. **連続防止ロジックの緩和**: スコア順を崩さないバケットシャッフルへの変更を検討

### 未作成ファイル
7. **AGENTS.md / CLAUDE.md / GEMINI.md**: エージェント設定ファイル（プロジェクトルールの正本）
8. **カテゴリページ（/social/ 等）**: Phase3で対応
9. **VIBRA_REBOOT自身のRSS生成**: Phase3で対応

### 確認不足
10. **実際のYahoo!ニュースRSS取得テスト**: ローカルでpipeline.pyを実行して動作確認が必要
11. **GitHub Actionsの動作確認**: 初回手動実行後、エラーログの確認が必要
12. **スマホ実機テスト**: スワイプ動作・表示崩れの確認

---

【7. 次のチャットで最初に依頼すべき内容】

以下の依頼文を新しいチャットの先頭に貼ってください：

---

【引き継ぎ】VIBRA_REBOOT（ScrollNow）Phase2完了 → デプロイ準備

前チャットでVIBRA_REBOOTのPhase2（SEO/AIO対策・個別記事ページ生成）まで完全実装しました。以下のファイル群を `/mnt/agents/output/` に保存済みです。

**保存済みファイル（20ファイル）:**
- pipeline.py（Phase2完全実装版：generate_article_pages + cleanup_old_articles + sitemap.xml個別ページURL追加）
- template.html（JSON-LD + メタタグ最適化版）
- template_article.html（個別記事ページテンプレート：NewsArticle JSON-LD + OGP + Twitter Card）
- update.yml（毎時更新：article/*.html コミット含む）
- cleanup.yml（毎日午前3時：90日超過記事削除）
- robots.txt
- フック辞書11ファイル（shock〜money: 40本×7 + food〜entertainment: 30本×4 = 400本）
- DEPLOY_CHECKLIST.md（デプロイ前最終チェックリスト）
- PHASE2_ARTICLE_PAGES_v2.md（設計案）

**設計思想（変更不可）:**
- LLM禁止（フック・要約・感情分類はすべてルールベース）
- UX保護（フィードから個別記事ページへの導線なし）
- 供給量抑制（1回10件）
- Layer分離（Layer1=ユーザー、Layer2=Google/AI）

**未解決・次のステップ:**
1. 全ファイルを一括ZIP化してダウンロード可能にする
2. デプロイ手順書の作成（GitHub Settings → Pages/Actions有効化のステップバイステップ）
3. AGENTS.md / CLAUDE.md / GEMINI.md の作成（エージェント設定ファイル）
4. または、上記1〜3のうち優先度を指定して実行

**依頼:** 上記のうち、まず「全ファイルの一括ZIP化」と「デプロイ手順書の作成」をお願いします。または、優先度を変更したい場合は指示してください。

---

【8. 引き継ぎ本文】

以下、新しいチャットの先頭にそのまま貼れる完成形です：

---

# VIBRA_REBOOT（ScrollNow）Phase2完了 引き継ぎ

## プロジェクト概要
VIBRA_REBOOTは「ニュースアプリではなくTikTokのようにスワイプするニュース消費体験」をGitHub Pagesで永久運用するプロジェクトです。Phase2（SEO/AIO対策・個別記事ページ生成）まで完全実装済み。

## 設計思想（変更不可）
1. **LLM禁止**: フック生成・要約・感情分類はすべてルールベース（外部JSON辞書 + キーワード判定）
2. **UX保護**: フィード（index.html）から個別記事ページへの導線は設けない。スワイプ体験を壊さない
3. **供給量抑制**: 1回あたり10件程度。過剰供給より情報密度を重視
4. **Layer分離**: Layer1（ユーザー/TikTok体験）と Layer2（Google/SEO資産）と Layer3（AI/JSON-LD）を分離

## 技術仕様（確定）
- **ニュースソース**: Yahoo!ニュース RSS（APIキー不要・無料）
- **配信**: GitHub Pages（完全無料・サーバーレス）
- **自動更新**: GitHub Actions（cron: '0 * * * *'、1時間ごと）
- **フック総数**: 400本（11感情カテゴリ：shock/anger/curiosity/empathy/fear/impact/money/food/game/anime/entertainment）
- **個別記事URL**: `/article/{YYYYMMDD}-{HHMMSS}-{genre}-{seq:03d}.html`
- **保持期間**: 90日（cleanup.ymlで毎日午前3時自動削除）
- **description**: `hook + title`（AI要約禁止・LLM導入の誘惑を断つ設計）
- **sitemap.xml**: 自動生成（index.html priority=1.0 + article/*.html priority=0.6、最大5000件）

## 保存済みファイル（20ファイル、/mnt/agents/output/）
| ファイル | 内容 |
|:---|:---|
| pipeline.py | Phase2完全実装版（26KB）。generate_article_pages() + cleanup_old_articles() + sitemap.xml個別ページURL追加 |
| template.html | フィードテンプレート。JSON-LD（WebSite+NewsMediaOrganization）+ title/description最適化 |
| template_article.html | 個別記事ページテンプレート。NewsArticle JSON-LD + OGP + Twitter Card + ダークテーマ |
| update.yml | 毎時更新Actions。index.html + sitemap.xml + robots.txt + article/*.html をコミット |
| cleanup.yml | 毎日午前3時実行。90日超過のarticle/*.htmlを削除 |
| robots.txt | クロール制御 + Sitemap参照 |
| shock.json | 40本 |
| anger.json | 40本 |
| curiosity.json | 40本 |
| empathy.json | 40本 |
| fear.json | 40本 |
| impact.json | 40本 |
| money.json | 40本 |
| food.json | 30本（新規） |
| game.json | 30本（新規） |
| anime.json | 30本（新規） |
| entertainment.json | 30本（新規） |
| keywords.json | 11カテゴリのキーワードマッピング |
| direct_map.json | 50個の強ワード→フック直接固定 |
| DEPLOY_CHECKLIST.md | デプロイ前最終チェックリスト |
| PHASE2_ARTICLE_PAGES_v2.md | Phase2設計案（修正版：URL連番・90日保持・hook+title） |

## 不採用項目（確定・変更しない）
- FAQPage（薄いページ大量発生リスク）
- フィード→記事導線（UX保護）
- AI要約/LLM導入（設計思想「LLM禁止」）
- 隠しテキスト（Googleペナルティリスク）
- 5000文字記事（TikTok体験崩壊）
- 日本語slug（崩壊リスク）

## 未解決・次のステップ
1. **全ファイルの一括ZIP化**（ダウンロード用）
2. **デプロイ手順書作成**（GitHub Settings → Pages/Actions有効化のステップバイステップ）
3. **AGENTS.md / CLAUDE.md / GEMINI.md作成**（エージェント設定ファイル）
4. **背景画像生成**（IMAGE_PROMPTS.md参照、11枚。なくてもCSS代替で動作）
5. **ローカル動作確認**（pipeline.pyの実行テスト）
6. **GitHub Actions動作確認**（初回手動実行後のエラーログ確認）
7. **スマホ実機テスト**（スワイプ動作・表示崩れ確認）

## 依頼
上記のうち、まず「全ファイルの一括ZIP化」と「デプロイ手順書の作成」をお願いします。優先度を変更したい場合は指示してください。

---
