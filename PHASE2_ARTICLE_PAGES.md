# VIBRA_REBOOT Phase2 設計案：個別記事ページ

> SEO/AIO会議の結論に基づく資産化設計
> 実装時期：Phase1運用開始後、データ蓄積に応じて

---

## 設計思想

**「ユーザー体験（Layer1）」を壊さずに「SEO資産（Layer2）」を増やす**

- index.html は「フィード」として維持（スワイプ体験の本丸）
- 個別ページは「裏側の資産」として生成（Googleがクロールする静的ページ）
- ユーザーが個別ページに直接アクセスすることは想定しない（フィードからの導線なし）

---

## URL設計

```
https://littlefunction.github.io/ScrollNow/
├── index.html                    # フィード（本丸）
├── article/
│   ├── 20260606-143000-shock-ai-news.html
│   ├── 20260606-143000-money-tax-increase.html
│   └── ...
├── sitemap.xml                   # 自動生成
├── robots.txt                    # 静的
└── ...
```

### URL命名規則

```
/article/{YYYYMMDD}-{HHMMSS}-{emotion}-{slug}.html
```

| 要素 | 例 | 説明 |
|:---|:---|:---|
| YYYYMMDD | 20260606 | 取得日 |
| HHMMSS | 143000 | 取得時刻 |
| emotion | shock, money, anger | 感情分類 |
| slug | ai-news, tax-increase | タイトルから自動生成 |

---

## 個別ページの構造

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <title>{タイトル} — ScrollNow</title>
  <meta name="description" content="{3行要約}">
  <!-- NewsArticle JSON-LD -->
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
    "description": "{3行要約}",
    "mainEntityOfPage": {"@type": "WebPage", "@id": "{URL}"},
    "image": "{ogp画像URL}"
  }
  </script>
</head>
<body>
  <h1>{フック}</h1>
  <h2>結論</h2>
  <p>{3行要約}</p>
  <h2>詳細</h2>
  <p>{本文要約}</p>
  <h2>出典</h2>
  <a href="{元URL}" target="_blank">{元サイト名}</a>
  <hr>
  <a href="/">← ScrollNow フィードに戻る</a>
</body>
</html>
```

---

## pipeline.py への追加実装案

```python
def generate_article_page(article: Article, timestamp: str) -> str:
    slug = re.sub(r'[^\w]', '-', article.title)[:30]
    filename = f"article/{timestamp}-{article.emotion}-{slug}.html"
    # template_article.html を読み込んで置換
    ...
    return filename

# fetch_news() 内で各記事に対して生成
for art in articles:
    page_path = generate_article_page(art, now.strftime("%Y%m%d-%H%M%S"))
    art.local_url = page_path

# sitemap.xml に個別ページURLを追加
```

---

## 運用ルール

| 項目 | 方針 |
|:---|:---|
| ページ寿命 | 30日間保持 → 30日後は自動削除（sitemap.xmlから除外） |
| 重複防止 | 同じタイトルは上書き（slugで判定） |
| OGP画像 | ジャンル背景画像を流用（/assets/bg_{genre}.png） |
| 内部リンク | フィード → 個別ページの導線は**設けない**（UX保護） |
| 外部リンク | 元記事へのリンクを必須（著作権・信頼性） |

---

## 期待される効果

| 指標 | 効果 |
|:---|:---|
| Google検索 | 個別ページがインデックスされ、検索キーワードで露出 |
| AI Overview | NewsArticle JSON-LD が引用ソースとして認識される |
| ドメイン権威 | ページ数が増え、ドメインの「新鮮さ」スコア向上 |
| 長期資産 | 過去の記事が「アーカイブ」として機能 |

---

## 実装コスト

| 項目 | 工数 | 難易度 |
|:---|:---|:---|
| template_article.html 作成 | 1h | 低 |
| generate_article_page() 実装 | 2h | 中 |
| sitemap.xml 動的更新 | 1h | 低 |
| 30日後自動削除 | 2h | 中 |
| **合計** | **6h** | **低〜中** |
