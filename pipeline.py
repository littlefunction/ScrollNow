import re, random, requests, json, os, html
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Tuple, Dict
from pathlib import Path
import datetime

RSS_FEEDS = {
    "社会": "https://news.yahoo.co.jp/rss/topics/domestic.xml",
    "国際": "https://news.yahoo.co.jp/rss/topics/world.xml",
    "経済": "https://news.yahoo.co.jp/rss/topics/business.xml",
    "テクノロジー": "https://news.yahoo.co.jp/rss/topics/it.xml",
    "スポーツ": "https://news.yahoo.co.jp/rss/topics/sports.xml",
    "エンタメ": "https://news.yahoo.co.jp/rss/topics/entertainment.xml",
    "グルメ": "https://news.yahoo.co.jp/rss/topics/food.xml",
    "ゲーム": "https://news.yahoo.co.jp/rss/topics/game.xml",
    "アニメ": "https://news.yahoo.co.jp/rss/topics/anime.xml",
}

GENRE_CONFIG = {
    "社会": {"bg": "assets/bg_society.png", "color": "#FF2D55", "emoji": "🚨"},
    "国際": {"bg": "assets/bg_world.png", "color": "#5856D6", "emoji": "🌍"},
    "経済": {"bg": "assets/bg_economy.png", "color": "#FF9500", "emoji": "💰"},
    "テクノロジー": {"bg": "assets/bg_tech.png", "color": "#007AFF", "emoji": "📱"},
    "スポーツ": {"bg": "assets/bg_sports.png", "color": "#34C759", "emoji": "⚽"},
    "一般": {"bg": "assets/default.png", "color": "#8E8E93", "emoji": "📰"},
    "AD": {"bg": "assets/bg_ad.png", "color": "#FF0050", "emoji": "📢"},
    "TOP5": {"bg": "assets/default.png", "color": "#FFD700", "emoji": "🔥"},
    "エンタメ": {"bg": "assets/bg_entertainment.png", "color": "#FF3B30", "emoji": "🎬"},
    "グルメ": {"bg": "assets/bg_food.png", "color": "#FFCC00", "emoji": "🍜"},
    "ゲーム": {"bg": "assets/bg_game.png", "color": "#8E44FF", "emoji": "🎮"},
    "アニメ": {"bg": "assets/bg_anime.png", "color": "#FF66CC", "emoji": "📺"},
}

# --- Phase2.5+: ジャンル英語表記（URL安全） ---
GENRE_SLUG = {
    "社会": "society",
    "国際": "world",
    "経済": "economy",
    "テクノロジー": "tech",
    "スポーツ": "sports",
    "エンタメ": "entertainment",
    "グルメ": "food",
    "ゲーム": "game",
    "アニメ": "anime",
    "一般": "general",
    "AD": "ad",
    "TOP5": "top5",
}
# ---------------------------------------------

# --- Phase2.5+: 広告スロット（検索キーワード方式・自動運転） ---
# 商品固定URLではなく楽天検索結果URL。1週間固定ローテーション。
AD_SLOTS = {
    "money": {
        "genre": "money",
        "background": "assets/bg_economy.png",
        "hooks": ["電気代高すぎない？", "最近これ買う人増えてる", "知らないと損する"],
        "body_lines": ["最近、", "節約グッズを探す人が増えています。"],
        "cta": "人気商品を見る →",
        "search_keywords": ["節電グッズ", "防災用品", "収納グッズ"],
    },
    "food": {
        "genre": "food",
        "background": "assets/bg_food.png",
        "hooks": ["これ食べた？", "売り切れ前に", "話題の味"],
        "body_lines": ["今週、", "ご当地グルメが注目されています。"],
        "cta": "人気商品を見る →",
        "search_keywords": ["ご当地ラーメン", "冷凍食品", "訳ありスイーツ"],
    },
    "game": {
        "genre": "game",
        "background": "assets/bg_game.png",
        "hooks": ["売り切れる前に", "これ知ってる？", "人気上昇中"],
        "body_lines": ["今、", "ゲーミング用品が売れています。"],
        "cta": "人気商品を見る →",
        "search_keywords": ["Switch周辺機器", "ゲーミング用品", "モバイルバッテリー"],
    },
}

# 感情→広告ジャンルのマッピング
EMOTION_TO_AD = {
    "shock": "money",
    "anger": "money",
    "fear": "money",
    "curiosity": "game",
    "empathy": "food",
    "impact": "money",
    "money": "money",
    "entertainment": "game",
    "food": "food",
    "game": "game",
    "anime": "game",
}

def get_ad_config(emotion: str) -> dict:
    """感情に応じた広告スロットを取得。1週間固定ローテーション。"""
    ad_genre = EMOTION_TO_AD.get(emotion, "money")
    slot = AD_SLOTS[ad_genre]

    # 1週間固定ローテーション（ISO週番号ベース）
    week_num = datetime.datetime.now().isocalendar()[1]
    keyword_idx = week_num % len(slot["search_keywords"])
    keyword = slot["search_keywords"][keyword_idx]

    # 楽天アフィリエイトID・アプリケーションIDを環境変数から取得
    affiliate_id = os.environ.get("RAKUTEN_AFFILIATE_ID", "")
    app_id = os.environ.get("RAKUTEN_APP_ID", "")

    # 検索URL生成（アフィリエイトID付与）
    base_url = f"https://search.rakuten.co.jp/search/mall/{keyword}/"
    params = []
    if affiliate_id:
        params.append(f"scid={affiliate_id}")
    if app_id:
        params.append(f"sitem={app_id}")

    if params:
        url = f"{base_url}?{'&'.join(params)}"
    else:
        url = base_url

    # フックはランダム選択（重複回避簡易版）
    hook = random.choice(slot["hooks"])

    return {
        "genre": slot["genre"],
        "background": slot["background"],
        "hook": hook,
        "body_lines": slot["body_lines"],
        "cta": slot["cta"],
        "url": url,
        "keyword": keyword,
    }
# ---------------------------------------------

@dataclass
class Article:
    title: str
    body: str
    genre: str
    url: str
    summary: str = ""
    hook: str = ""
    emotion: str = "shock"
    catch: Tuple[str, str] = ("", "")
    score: int = 0

class HookEngine:
    def __init__(self, hooks_dir: str = "hooks"):
        self.hooks_dir = Path(hooks_dir)
        self.hooks: Dict[str, List[str]] = {}
        self.keywords: Dict[str, List[str]] = {}
        self.direct_map: Dict[str, str] = {}
        self.recent_hooks: List[str] = []
        self._load()

    def _load(self):
        emotions = ["shock", "anger", "fear", "curiosity", "empathy", "impact", "money", "entertainment", "food", "game", "anime"]
        for emotion in emotions:
            path = self.hooks_dir / f"{emotion}.json"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    self.hooks[emotion] = json.load(f)
            else:
                print(f"    [WARN] {emotion}.json not found — using shock fallback")
                self.hooks[emotion] = []

        kw_path = self.hooks_dir / "keywords.json"
        if kw_path.exists():
            with open(kw_path, "r", encoding="utf-8") as f:
                self.keywords = json.load(f)

        dm_path = self.hooks_dir / "direct_map.json"
        if dm_path.exists():
            with open(dm_path, "r", encoding="utf-8") as f:
                self.direct_map = json.load(f)

        total = sum(len(v) for v in self.hooks.values())
        print(f"    [HookEngine] {total} hooks, {sum(len(v) for v in self.keywords.values())} keywords, {len(self.direct_map)} direct maps")

    def detect_emotion(self, title: str, body: str) -> str:
        combined = title + " " + body[:200]
        scores = {emotion: 0 for emotion in self.keywords.keys()}

        for emotion, keywords in self.keywords.items():
            for kw in keywords:
                scores[emotion] += combined.count(kw)

        if any(w in combined for w in ["逮捕", "死亡", "死去", "事故死", "殺人"]):
            scores["impact"] += 5
        if any(w in combined for w in ["億円", "兆円", "補助金", "予算", "税金"]):
            scores["money"] += 5
        if any(w in combined for w in ["不正", "脱税", "横領", "増税", "値上げ"]):
            scores["anger"] += 3
        if any(w in combined for w in ["地震", "台風", "警報", "避難"]):
            scores["fear"] += 3

        return max(scores, key=scores.get) if max(scores.values()) > 0 else "shock"

    def get_hook(self, title: str, body: str, score: int = 0) -> str:
        combined = title + " " + body[:100]

        for keyword, fixed_hook in self.direct_map.items():
            if keyword in combined:
                if fixed_hook not in self.recent_hooks:
                    self._register_hook(fixed_hook)
                    return fixed_hook

        emotion = self.detect_emotion(title, body)
        hooks = self.hooks.get(emotion, self.hooks.get("shock", ["知らない人多すぎる"]))
        if not hooks:
            hooks = self.hooks.get("shock", ["知らない人多すぎる"])

        candidates = [h for h in hooks if h not in self.recent_hooks]
        if not candidates:
            candidates = hooks

        if score >= 8:
            short_candidates = [h for h in candidates if 4 <= len(h) <= 6]
            if short_candidates:
                candidates = short_candidates

        hook = random.choice(candidates) if candidates else "知らない人多すぎる"
        self._register_hook(hook)
        return hook

    def _register_hook(self, hook: str):
        self.recent_hooks.append(hook)
        if len(self.recent_hooks) > 5:
            self.recent_hooks.pop(0)

HOOK_ENGINE = HookEngine()

def fetch_article_body(url: str) -> str:
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        article = soup.find("article") or soup.find("div", class_=re.compile("article|content|main"))
        if article:
            paragraphs = article.find_all("p")
            text = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 10])
            return text[:500]
        all_p = soup.find_all("p")
        text = " ".join([p.get_text().strip() for p in all_p if len(p.get_text().strip()) > 20])
        return text[:500]
    except Exception as e:
        print(f"    [BODY ERR] {url[:50]}...: {e}")
        return ""

def generate_result_summary(title: str, body: str) -> str:
    combined = title + " " + body[:200]
    result_patterns = [
        (r'(\d+)億円', r'\1億円が動いた'),
        (r'(\d+)万人', r'\1万人が影響を受ける'),
        (r'値上げ', '値上げが決定した'),
        (r'閉鎖', '閉鎖が決まった'),
        (r'廃止', '廃止される'),
        (r'禁止', '禁止される'),
        (r'義務化', '義務化される'),
        (r'規制', '規制が強化される'),
    ]
    for pattern, replacement in result_patterns:
        if re.search(pattern, combined):
            return re.sub(pattern, replacement, title)[:40]
    sentences = [s.strip() for s in re.split(r'(?<=[。！？])', body) if len(s.strip()) >= 5]
    if sentences:
        return sentences[-1][:35]
    return title[:35]

def calculate_score(title: str, body: str) -> int:
    score = 0
    text = title + body[:200]
    important = {
        "逮捕":5, "書類送検":4, "死亡":5, "億円":4, "兆円":5,
        "地震":4, "台風":3, "破綻":4, "不正":3, "閉鎖":3,
        "値上げ":2, "AI":3, "ハッキング":4, "戦争":5, "核":5,
        "補助金":3, "予算":3, "税金":3, "増税":4,
        "結婚":4, "熱愛":5, "活動休止":5, "引退":5, "炎上":4,
        "限定":3, "新商品":3, "人気":2, "ランキング":3, "売り切れ":4,
        "サービス終了":5, "新キャラ":4, "アプデ":3,
        "続編":4, "制作決定":5, "最終回":5,
    }
    for word, pt in important.items():
        if word in text:
            score += pt
    numbers = re.findall(r'\d+', text)
    score += len(numbers)
    score += text.count("！") + text.count("？") * 2
    return score

SAVE_CATCHES = {
    "shock": ("知らないと", "損する"),
    "anger": ("知らないと", "怒る"),
    "fear": ("知らないと", "危険"),
    "curiosity": ("先に知る", "人勝ち"),
    "empathy": ("共感", "しかない"),
    "impact": ("知らないと", "損する"),
    "money": ("お金に関わる", "話"),
    "entertainment": ("話題", "沸騰中"),
    "food": ("保存して", "後で行く"),
    "game": ("あとで遊ぶ", "保存推奨"),
    "anime": ("あとで見る", "保存案件"),
}

def make_save_catch(emotion: str) -> Tuple[str, str]:
    return SAVE_CATCHES.get(emotion, ("知らないと", "損する"))

def fetch_news(limit=10) -> List[Article]:
    articles = []
    ua = {"User-Agent": "Mozilla/5.0"}
    for genre, url in RSS_FEEDS.items():
        try:
            r = requests.get(url, timeout=10, headers=ua)
            soup = BeautifulSoup(r.text, "xml")
            items = soup.find_all("item")[:4]
            for item in items:
                title = item.find("title").text
                link = item.find("link").text
                body = fetch_article_body(link)
                if not body:
                    body = title

                score = calculate_score(title, body)
                hook = HOOK_ENGINE.get_hook(title, body, score)
                emotion = HOOK_ENGINE.detect_emotion(title, body)
                summary = generate_result_summary(title, body)
                catch = make_save_catch(emotion)

                articles.append(Article(title, body, genre, link, summary, hook, emotion, catch, score))
        except Exception as e:
            print(f"[WARN] {genre} fetch failed: {e}")
            continue

    articles.sort(key=lambda x: x.score, reverse=True)
    top_articles = articles[:limit]
    random.shuffle(top_articles)

    # --- 連続防止（感情優先 → ジャンル副次） ---
    def _no_consecutive(items, key_func, max_attempts=100):
        """key_func(item) が同じ値が連続しないように並び替え"""
        result = []
        remaining = items[:]
        attempts = 0
        while remaining and attempts < max_attempts:
            placed = False
            for i, item in enumerate(remaining):
                if not result or key_func(result[-1]) != key_func(item):
                    result.append(remaining.pop(i))
                    placed = True
                    break
            if not placed:
                # どうしても連続が避けられない場合はそのまま追加
                result.append(remaining.pop(0))
            attempts += 1
        return result

    # ① 感情連続防止（最重要）
    top_articles = _no_consecutive(top_articles, lambda a: a.emotion)
    # ② ジャンル連続防止（副次）
    top_articles = _no_consecutive(top_articles, lambda a: a.genre)
    # ---------------------------------------------

    return top_articles

# --- Phase2+: 個別記事ページ生成 ---

def generate_article_pages(articles: List[Article], timestamp: str) -> List[str]:
    """
    個別記事ページを生成。
    URL: /article/{YYYYMMDD}-{HHMMSS}-{genre}-{seq:03d}.html
    """
    Path("article").mkdir(exist_ok=True)
    generated = []
    seq_map: Dict[str, int] = {}

    with open("template_article.html", "r", encoding="utf-8") as f:
        template = f.read()

    for art in articles:
        seq_map[art.genre] = seq_map.get(art.genre, 0) + 1
        seq = seq_map[art.genre]
        genre_en = GENRE_SLUG.get(art.genre, "general")
        filename = f"article/{timestamp}-{genre_en}-{seq:03d}.html"

        # description = hook + title（AI要約禁止）
        description = f"{art.hook}。{art.title}"
        conf = GENRE_CONFIG.get(art.genre, GENRE_CONFIG["一般"])
        now_iso = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")
        now_display = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M")

        page_html = (template
            .replace("{{TITLE}}", html.escape(art.title))
            .replace("{{DESCRIPTION}}", html.escape(description))
            .replace("{{HOOK}}", html.escape(art.hook))
            .replace("{{SUMMARY}}", html.escape(art.summary))
            .replace("{{GENRE}}", html.escape(art.genre))
            .replace("{{GENRE_EMOJI}}", conf.get("emoji", "📰"))
            .replace("{{GENRE_COLOR}}", conf.get("color", "#8E8E93"))
            .replace("{{EMOTION}}", html.escape(art.emotion))
            .replace("{{SCORE}}", str(art.score))
            .replace("{{SOURCE_URL}}", html.escape(art.url))
            .replace("{{SOURCE_NAME}}", "Yahoo!ニュース")
            .replace("{{DATE_PUBLISHED}}", now_iso)
            .replace("{{DATE_MODIFIED}}", now_iso)
            .replace("{{DATE_DISPLAY}}", now_display)
            .replace("{{CANONICAL_URL}}", f"https://littlefunction.github.io/ScrollNow/{filename}")
            .replace("{{OG_IMAGE}}", f"https://littlefunction.github.io/ScrollNow/{conf.get('bg', 'assets/default.png')}")
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(page_html)
        generated.append(filename)

    print(f"    -> {len(generated)} article pages generated")
    return generated


def cleanup_old_articles(days: int = 90):
    """90日以上前の article/ を削除"""
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    article_dir = Path("article")
    if not article_dir.exists():
        return
    removed = 0
    for path in article_dir.glob("*.html"):
        try:
            date_str = path.stem[:8]
            file_date = datetime.datetime.strptime(date_str, "%Y%m%d")
            if file_date < cutoff:
                path.unlink()
                removed += 1
        except ValueError:
            continue
    if removed > 0:
        print(f"    -> {removed} old article pages removed (> {days} days)")

# ---------------------------------------------

def build_cards(items: List[dict]) -> str:
    parts = []
    for item in items:
        conf = GENRE_CONFIG.get(item['genre'], GENRE_CONFIG["一般"])
        is_ad = item['type'] == 'ad'
        is_loop = item['type'] == 'loop'

        cta = ''
        if not is_ad and not is_loop and item['url'] != '#':
            cta = f'<a href="{item["url"]}" class="card-link" target="_blank" rel="noopener">続きを読む →</a>'

        ad_btn = ''
        if is_ad:
            ad_btn = f'<a href="{item["url"]}" class="ad-cta" target="_blank" rel="noopener">{item.get("cta", "人気商品を見る →")}</a>'

        # --- Phase2.5+: 広告カード構造 ---
        if is_ad:
            # 商品画像透過重ね（背景の一部として）
            product_overlay = ''
            if item.get('product_image'):
                product_overlay = f'<div class="ad-product-overlay"><img src="{item["product_image"]}" alt="" loading="lazy"></div>'

            # 次の記事予告
            next_preview = ''
            if item.get('next_preview'):
                next_preview = f'<div class="next-preview">次：「{item["next_preview"]}…」</div>'

            # 本文2行（改行重視）
            body_html = ''
            if item.get('body_lines'):
                body_html = '<div class="ad-body">' + ''.join([f'<p>{line}</p>' for line in item['body_lines']]) + '</div>'

            card = (
                f'<div class="card" data-type="ad" style="background-image: url(\'{conf["bg"]}\')">'
                f'<div class="genre-banner" style="background-color: {conf["color"]}">'
                f'{conf["emoji"]} PR'
                f'</div>'
                f'<div class="hook-main">{item.get("hook", "")}</div>'
                f'{body_html}'
                f'{product_overlay}'
                f'{ad_btn}'
                f'{next_preview}'
                f'</div>'
            )
        # ---------------------------------
        elif is_loop:
            card = (
                f'<div class="card" data-type="loop" style="background-image: url(\'{conf["bg"]}\')">'
                f'<div class="genre-banner" style="background-color: {conf["color"]}">'
                f'{conf["emoji"]} {item["genre"]}'
                f'</div>'
                f'<div class="loop-text">'
                f'{item["summary"]}'
                f'<div class="loop-sub">↑ スワイプで最初に戻る</div>'
                f'</div>'
                f'</div>'
            )
        elif item['type'] == 'top5':
            card = (
                f'<div class="card" data-type="top5" style="background-image: url(\'{conf["bg"]}\')">'
                f'<div class="genre-banner" style="background-color: {conf["color"]}">'
                f'{conf["emoji"]} {item["genre"]}'
                f'</div>'
                f'<div class="hook-main">{item["hook"]}</div>'
                f'<div class="summary-sub">{item["summary"]}</div>'
                f'<div class="catch-text">'
                f'<span>{item["catch1"]}</span>'
                f'<span>{item["catch2"]}</span>'
                f'</div>'
                f'<div class="top5-hint" onclick="openTop5()">タップしてランキングを見る →</div>'
                f'</div>'
            )
        else:
            hook_html = f'<div class="hook-main">{item.get("hook", "")}</div>' if not is_ad and item.get("hook") else ''
            summary_html = f'<div class="summary-sub">{item["summary"]}</div>' if not is_ad else ''

            card = (
                f'<div class="card" data-type="{item["type"]}" style="background-image: url(\'{conf["bg"]}\')">'
                f'<div class="genre-banner" style="background-color: {conf["color"]}">'
                f'{conf["emoji"]} {item["genre"]}'
                f'</div>'
                f'{hook_html}'
                f'{summary_html}'
                f'<div class="catch-text">'
                f'<span>{item["catch1"]}</span>'
                f'<span>{item["catch2"]}</span>'
                f'</div>'
                f'{cta}'
                f'</div>'
            )
        parts.append(card)
    return "\n".join(parts)

if __name__ == "__main__":
    print("[1/5] フックエンジン初期化中...")
    print(f"    -> {sum(len(v) for v in HOOK_ENGINE.hooks.values())} hooks, {sum(len(v) for v in HOOK_ENGINE.keywords.values())} keywords, {len(HOOK_ENGINE.direct_map)} direct maps")

    print("[2/5] ニュース取得中...")
    news_arts = fetch_news(10)
    print(f"    -> {len(news_arts)}件取得")

    top5 = sorted(news_arts, key=lambda x: x.score, reverse=True)[:5]
    top5_data = [{"title": html.escape(a.title), "genre": a.genre, "url": a.url, "score": a.score, "emotion": a.emotion, "hook": a.hook} for a in top5]

    print("[3/5] カード構築中...")
    final_list = []
    ad_inserted = 0
    for i, art in enumerate(news_arts):
        final_list.append({
            "type": "news",
            "genre": art.genre,
            "summary": art.summary,
            "hook": art.hook,
            "emotion": art.emotion,
            "catch1": art.catch[0],
            "catch2": art.catch[1],
            "url": art.url,
            "score": art.score,
        })
        # --- Phase2.5+: 広告挿入（感情連動・3件ごと） ---
        if (i + 1) % 3 == 0 and i != len(news_arts) - 1:
            prev_emotion = art.emotion
            ad_conf = get_ad_config(prev_emotion)

            # 次の記事のタイトルを30〜50%だけ予告
            next_idx = i + 1
            next_preview = ""
            if next_idx < len(news_arts):
                next_title = news_arts[next_idx].title
                preview_len = max(5, len(next_title) // 3)  # 30〜50%
                next_preview = next_title[:preview_len]

            final_list.append({
                "type": "ad",
                "genre": ad_conf["genre"],
                "hook": ad_conf["hook"],
                "body_lines": ad_conf["body_lines"],
                "cta": ad_conf["cta"],
                "url": ad_conf["url"],
                "product_image": "",  # 将来: 商品画像パス
                "next_preview": next_preview,
            })
            ad_inserted += 1
        # -------------------------------------------------

    # Phase2+: TOP5ランキングカードを最後に配置（終了演出→継続演出）
    now = datetime.datetime.now()
    next_hour = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    minutes_until_next = int((next_hour - now).total_seconds() // 60)

    top5_card = {
        "type": "top5",
        "genre": "TOP5",
        "summary": f"🔥 今日の重要ニュース\n次の更新まであと{minutes_until_next}分",
        "hook": "ランキングを見る",
        "emotion": "curiosity",
        "catch1": "タップして",
        "catch2": "確認",
        "url": "#",
        "score": 999,
    }
    final_list.append(top5_card)

    print("[4/5] HTML生成中...")
    cards_html = build_cards(final_list)
    top5_json = json.dumps(top5_data, ensure_ascii=False)

    with open("template.html", "r", encoding="utf-8") as f:
        template = f.read()

    html_out = template.replace("{{CARDS}}", cards_html).replace("{{TOP5_JSON}}", top5_json)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_out)

    # --- Phase2+: 個別記事ページ生成 ---
    print("[4.5/5] 個別記事ページ生成中...")
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    generate_article_pages(news_arts, timestamp)
    # ---------------------------------------------

    # --- Phase1+: sitemap.xml 自動生成（個別ページURL含む） ---
    print("[5/5] sitemap.xml / robots.txt 生成中...")
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+09:00")

    article_urls = []
    if Path("article").exists():
        for path in sorted(Path("article").glob("*.html")):
            try:
                date_str = path.stem[:8]
                file_date = datetime.datetime.strptime(date_str, "%Y%m%d")
                article_urls.append((
                    f"https://littlefunction.github.io/ScrollNow/{path}",
                    file_date.strftime("%Y-%m-%dT%H:%M:%S+09:00")
                ))
            except ValueError:
                continue

    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        '    <loc>https://littlefunction.github.io/ScrollNow/</loc>',
        f'    <lastmod>{now_iso}</lastmod>',
        '    <changefreq>hourly</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
    ]
    for url, lastmod in article_urls[:5000]:
        sitemap_lines.extend([
            '  <url>',
            f'    <loc>{url}</loc>',
            f'    <lastmod>{lastmod}</lastmod>',
            '    <changefreq>daily</changefreq>',
            '    <priority>0.6</priority>',
            '  </url>',
        ])
    sitemap_lines.append('</urlset>')

    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap_lines))
    print(f"    -> sitemap.xml generated ({len(article_urls)} article URLs)")
    # ---------------------------------------------

    # --- Phase2+: 古い記事ページを削除（90日保持） ---
    print("[5.5/5] 古い記事ページクリーンアップ...")
    cleanup_old_articles(days=90)
    # ---------------------------------------------

    print("✅ index.html + article pages generated successfully.")
    print(f"   ニュース: {len(news_arts)}件 | 広告: {ad_inserted}件 | TOP5: 5件")
    print(f"   フック辞書: {sum(len(v) for v in HOOK_ENGINE.hooks.values())}本")
