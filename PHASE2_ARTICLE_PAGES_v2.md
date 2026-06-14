# VIBRA_REBOOT Phase2 設計案（修正版 v2）

> プロデューサー・SEO・AIO・ディレクター・マーケ全員のフィードバック反映
> 実装時期：Phase1運用開始後、データ蓄積に応じて
> 方針：「実装しないで話だけ聞く」→ 設計を固める

---

## 設計思想（変更なし）

**「ユーザー体験（Layer1）」を壊さずに「SEO資産（Layer2）」を増やす**

- index.html は「フィード」として維持（スワイプ体験の本丸）
- 個別ページは「裏側の資産」として生成（Googleがクロールする静的ページ）
- **ユーザーが個別ページに直接アクセスすることは想定しない**（フィードからの導線なし）

---

## 修正点一覧（v1 → v2）

| 項目 | v1（旧案） | v2（修正版） | 修正理由 |
|:---|:---|:---|:---|
| **URL命名** | `20260606-143000-shock-ai-news.html` | `20260606-143000-tech-001.html` | 日本語slugが崩壊する危険を回避 |
| **保持期間** | 30日 | **90〜180日** | Googleインデックスサイクル（クロール→評価→反映）に時間がかかる |
| **description** | 3行要約 | **`{hook} + {title}`** | AI要約の誘惑を生まない。LLM導入の防波堤 |
| **FAQPage** | 検討 | **不採用** | 薄いページが大量発生するリスク |
| **フィード→記事導線** | 検討 | **不採用** | スワイプ体験から長文ページへの遷移で世界観が壊れる |

---

## URL設計（修正版）

```
https://littlefunction.github.io/ScrollNow/
├── index.html                    # フィード（本丸）
├── article/
│   ├── 20260606-143000-tech-001.html
│   ├── 20260606-143000-money-002.html
│   ├── 20260606-143000-sports-003.html
│   └── ...
├── sitemap.xml                   # 自動生成（Phase1済）
├── robots.txt                    # 静的（Phase1済）
└── ...
```

### URL命名規則（v2）

```
/article/{YYYYMMDD}-{HHMMSS}-{genre}-{seq:03d}.html
```

| 要素 | 例 | 説明 |
|:---|:---|:---|
| YYYYMMDD | 20260606 | 取得日 |
| HHMMSS | 143000 | 取得時刻（1時間ごと更新なので時刻は固定） |
| genre | tech, money, sports | ジャンル（英語表記・slug安全） |
| seq | 001, 002, 003 | **連番**（同一時刻内の記事順） |

### なぜ連番か

日本語タイトルからのslug生成：

```python
# 危険な例（v1）
slug = re.sub(r"[^\w]", "-", "大谷翔平が○○")  # → "--------" 崩壊
```

GoogleはURLの「美しさ」をそこまで重視しない。連番で十分。

---

## 個別ページの構造（修正版）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <!-- description = hook + title（AI要約禁止） -->
  <title>{タイトル} — ScrollNow</title>
  <meta name="description" content="{hook}。{title}">

  <!-- NewsArticle JSON-LD（AIO対策） -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": "{タイトル}",
    "datePublished": "{ISO8601}",
    "dateModified": "{ISO8601}",
    "author": {"@type": "Organization", "name": "ScrollNow"},
    "publisher": {
      "@type": "NewsMediaOrganization",
      "name": "ScrollNow",
      "logo": {"@type": "ImageObject", "url": "..."}
    },
    "description": "{hook}。{title}",
    "mainEntityOfPage": {"@type": "WebPage", "@id": "{URL}"},
    "image": "{ジャンル背景画像URL}"
  }
  </script>

  <!-- OGP -->
  <meta property="og:title" content="{hook} — {タイトル}">
  <meta property="og:description" content="{hook}。{title}">
  <meta property="og:image" content="{ジャンル背景画像URL}">
  <meta property="og:type" content="article">
</head>
<body>
  <!-- Layer2: Google向け（ユーザーが直接見ることは少ない） -->
  <article>
    <h1>{フック}</h1>
    <p>{タイトル}</p>
    <p>{本文要約（pipeline.pyで生成したsummaryを流用）}</p>
    <p><a href="{元URL}" target="_blank" rel="noopener">出典: {元サイト名}</a></p>
  </article>

  <hr>
  <a href="/">← ScrollNow フィードに戻る</a>
</body>
</html>
```

### description の設計意図

```text
【v1（旧案）】3行要約
→ 「結論：○○。理由：○○。今後：○○」
→ 将来的に「AIで要約しよう」となる誘惑を生む

【v2（修正版）】hook + title
→ 「何があった？大谷翔平が今季○○達成。」
→ シンプルで壊れない。LLM不要。
```

---

## 運用ルール（修正版）

| 項目 | v1 | v2（修正版） |
|:---|:---|:---|
| **ページ寿命** | 30日 | **90〜180日** |
| **重複防止** | slugで判定 | 連番で自然に回避 |
| **OGP画像** | ジャンル背景画像 | 同左 |
| **内部リンク** | フィード→個別ページ **なし** | 同左（UX保護） |
| **外部リンク** | 元記事へのリンク必須 | 同左（著作権・信頼性） |
| **FAQ構造** | 検討 | **不採用** |
| **AI要約** | 3行要約で暗黙的に必要 | **禁止**（hook+titleで完結） |

### なぜ90〜180日か

Googleのインデックスサイクル：

```text
生成（0日）
↓
クロール（1〜7日）
↓
評価（7〜30日）
↓
順位反映（30〜60日）
```

30日では「評価段階」で消える可能性がある。90日あれば「順位反映」まで確保できる。

---

## pipeline.py への追加実装案（修正版）

```python
def generate_article_pages(articles, timestamp):
    """
    個別記事ページを生成。
    URL: /article/{YYYYMMDD}-{HHMMSS}-{genre}-{seq:03d}.html
    """
    generated = []
    seq_map = {}  # ジャンルごとの連番

    for art in articles:
        seq_map[art.genre] = seq_map.get(art.genre, 0) + 1
        seq = seq_map[art.genre]
        genre_en = GENRE_SLUG.get(art.genre, 'general')  # ジャンル英語表記
        filename = f'article/{timestamp}-{genre_en}-{seq:03d}.html'

        # description = hook + title（AI要約禁止）
        description = f'{art.hook}。{art.title}'

        # template_article.html を読み込んで置換
        html = render_article_template(
            hook=art.hook,
            title=art.title,
            summary=art.summary,
            source_url=art.url,
            source_name='Yahoo!ニュース',
            genre=art.genre,
            emotion=art.emotion,
            description=description,
            bg_image=GENRE_CONFIG[art.genre]['bg'],
        )

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        generated.append(filename)

    return generated

# 90日後の自動削除（GitHub Actionsで毎日実行）
def cleanup_old_articles(days=90):
    """90日以上前の article/ を削除"""
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    for path in Path('article').glob('*.html'):
        # ファイル名から日付を抽出: 20260606-143000-tech-001.html
        date_str = path.stem[:8]
        file_date = datetime.datetime.strptime(date_str, '%Y%m%d')
        if file_date < cutoff:
            path.unlink()
            print(f'[CLEANUP] Removed {path}')
```

---

## 長期ビジョン（修正版）

### 数値シミュレーション

| 項目 | 値 |
|:---|:---|
| 1時間ごと更新 | 1回 |
| 1回あたり記事数 | 10〜15件 |
| 1日あたりページ生成 | 240〜360ページ |
| 保持期間 | 90日 |
| **総ページ数（常時）** | **≈ 2万ページ** |
| 1年間の累積生成数 | ≈ 9万ページ |

### GitHub Pages の制限との整合性

| 制限項目 | GitHub Pages制限 | 2万ページでの評価 |
|:---|:---|:---|
| リポジトリサイズ | 推奨1GB | 2万ページ ≈ 100〜200MB（十分余裕） |
| 帯域 | 100GB/月 | 静的HTMLなら十分 |
| ビルド時間 | 10分/回 | ページ生成は数秒 |
| **結論** | | **2万ページでも完全に収まる** |

### ScrollNow の本当の価値

```text
Phase1: ユーザーに「10枚のフィード」を提供
       ↓
Phase2: Googleに「2万ページのニュース資産」を提供
       ↓
数年後: ドメイン権威が蓄積
       ↓
       「ScrollNow」= 特定キーワードで引用される信頼ソース
```

---

## 不採用項目（再確認）

| 項目 | 不採用理由 |
|:---|:---|
| フィード→記事導線 | スワイプ体験から長文ページへの遷移で世界観崩壊 |
| FAQ大量生成 | 薄いページが大量発生。AIOにとっても価値が低い |
| AI要約（LLM） | 設計思想「LLM禁止」に反する。description=hook+titleで完結 |
| 隠しテキスト | Googleに見抜かれるリスク。ペナルティ対象 |
| 5000文字記事 | Wikipediaではない。TikTok体験が死ぬ |
| 日本語slug | 崩壊リスク。連番で十分 |

---

## 実装優先順位（最終版）

| 優先度 | 項目 | 工数 | 難易度 |
|:---|:---|:---|:---|
| S | template_article.html 作成 | 1h | 低 |
| S | generate_article_pages() 実装 | 2h | 中 |
| S | 90日後自動削除 | 2h | 中 |
| A | sitemap.xml に個別ページURLを追加 | 1h | 低 |
| A | OGPメタタグ最適化 | 1h | 低 |
| B | カテゴリページ（/social/ 等） | 4h | 中 |
| B | VIBRA_REBOOT自身のRSS生成 | 2h | 低 |
| **合計** | | **13h** | **低〜中** |

---

## 結論

この設計案の方向性は**かなり良い**。

- **index.html** = TikTok（ユーザー向け）
- **article/** = Google（検索エンジン向け）
- **90日保持** = インデックスサイクルを考慮した現実的な寿命
- **hook+title** = LLM導入の誘惑を断つシンプル設計
- **連番URL** = 日本語slug崩壊を回避する堅実な命名

数年後、ScrollNowの本当の価値は「10枚のフィード」ではなく、**裏で蓄積された数万ページのニュース資産**になる可能性が高い。