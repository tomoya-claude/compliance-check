#!/usr/bin/env python3
"""
コンプライアンスチェック Web アプリ
Streamlit で動作するブラウザベースのツール
"""

import streamlit as st
import csv
import io
import time
from googlesearch import search

# ネガティブワード一覧（カテゴリ別）
NEGATIVE_KEYWORDS = {
    "反社会的勢力": [
        "暴力団", "ヤクザ", "反社", "半グレ", "準構成員", "構成員",
        "フロント企業", "組長", "組員", "総会屋", "暴力団員",
        "反社会的勢力", "指定暴力団", "特殊知能暴力集団", "暴追",
        "組織犯罪", "マフィア", "闇社会", "暴力団排除", "暴排条例",
        "企業舎弟", "共生者", "密接交際者", "威力業務妨害",
    ],
    "刑事手続き": [
        "逮捕", "送検", "起訴", "容疑", "摘発", "検挙", "捜査",
        "指名手配", "釈放", "実刑", "有罪", "罰金", "懲役",
        "禁固", "書類送検", "略式起訴", "不起訴", "再逮捕",
        "取り調べ", "家宅捜索", "強制捜査", "任意同行",
        "公判", "判決", "求刑", "控訴", "上告", "保釈",
        "勾留", "拘留", "執行猶予", "前科", "前歴",
        "被疑者", "被告人", "犯人", "共犯", "主犯",
        "余罪", "再犯", "累犯", "初犯",
    ],
    "暴力・身体犯罪": [
        "暴行", "傷害", "殺人", "恐喝", "脅迫", "監禁",
        "誘拐", "強盗", "襲撃", "DV", "ストーカー",
        "器物損壊", "放火", "未遂", "強制わいせつ", "性的暴行",
        "致死", "致傷", "凶器", "殺害", "暴力",
        "虐待", "児童虐待", "ネグレクト", "傷害致死",
        "危険運転致死傷", "ひき逃げ", "あおり運転",
    ],
    "経済犯罪": [
        "詐欺", "横領", "着服", "窃盗", "収賄", "贈賄",
        "背任", "業務上横領", "特別背任", "架空請求",
        "振り込め詐欺", "投資詐欺", "マネーロンダリング",
        "資金洗浄", "闇金", "高利貸し", "出資法違反",
        "金融商品取引法違反", "不正送金", "持ち逃げ",
        "ポンジスキーム", "ネズミ講", "マルチ商法", "悪徳商法",
        "特定商取引法違反", "不正受給", "給付金詐欺",
        "保険金詐欺", "融資詐欺", "クレジットカード詐欺",
        "電子計算機使用詐欺", "オレオレ詐欺", "還付金詐欺",
        "ロマンス詐欺", "フィッシング詐欺", "なりすまし",
        "偽造", "変造", "文書偽造", "有印私文書偽造",
    ],
    "薬物犯罪": [
        "薬物", "覚醒剤", "大麻", "麻薬", "覚せい剤",
        "コカイン", "ヘロイン", "MDMA", "危険ドラッグ",
        "薬物所持", "薬物使用", "密売", "密輸",
        "向精神薬", "シンナー", "薬物密造", "薬物栽培",
        "大麻取締法", "覚醒剤取締法", "麻薬取締法",
        "薬物乱用", "注射器", "所持容疑",
    ],
    "財務・税務不正": [
        "脱税", "申告漏れ", "所得隠し", "粉飾決算", "粉飾",
        "架空取引", "循環取引", "不正会計", "簿外債務",
        "インサイダー", "インサイダー取引", "相場操縦",
        "有価証券報告書虚偽記載", "課徴金", "重加算税",
        "税務調査", "査察", "国税局", "追徴課税",
        "過少申告", "無申告", "仮装隠蔽", "二重帳簿",
        "裏金", "簿外取引", "飛ばし", "損失隠し",
        "利益操作", "売上水増し", "経費水増し",
        "架空経費", "架空売上", "不正経理",
    ],
    "法令違反・行政処分": [
        "違法", "違反", "不正", "偽装", "捏造", "改ざん",
        "行政処分", "行政指導", "業務停止", "業務改善命令",
        "営業停止", "免許取消", "許可取消", "是正勧告",
        "措置命令", "排除措置命令", "独占禁止法", "談合",
        "カルテル", "入札妨害", "不正入札", "下請法違反",
        "景品表示法違反", "優良誤認", "有利誤認",
        "不当表示", "誇大広告", "虚偽広告", "薬機法違反",
        "食品衛生法違反", "建築基準法違反", "消防法違反",
        "道路交通法違反", "廃棄物処理法違反", "不法投棄",
        "環境汚染", "公害", "産業廃棄物", "有害物質",
        "アスベスト", "土壌汚染", "水質汚染", "大気汚染",
    ],
    "訴訟・紛争・倒産": [
        "告訴", "告発", "訴訟", "損害賠償", "民事訴訟",
        "刑事告訴", "集団訴訟", "和解", "示談", "調停",
        "仮処分", "差押", "強制執行", "破産", "倒産",
        "民事再生", "会社更生", "債務不履行", "不渡り",
        "自己破産", "任意整理", "特別清算", "解散",
        "債務超過", "経営破綻", "資金繰り悪化", "手形不渡り",
        "取り立て", "競売", "担保権実行", "財産隠し",
    ],
    "ハラスメント・労務問題": [
        "パワハラ", "セクハラ", "モラハラ", "マタハラ",
        "ハラスメント", "いじめ", "嫌がらせ", "過労死",
        "過労", "長時間労働", "残業代未払い", "賃金未払い",
        "不当解雇", "労基法違反", "労働基準法違反",
        "安全配慮義務違反", "労災隠し", "偽装請負",
        "パタハラ", "カスハラ", "アルハラ", "アカハラ",
        "就活セクハラ", "リモハラ", "時短ハラスメント",
        "サービス残業", "名ばかり管理職", "固定残業代",
        "最低賃金違反", "36協定違反", "労働災害",
        "安全衛生法違反", "メンタルヘルス", "うつ病",
        "休職", "自殺", "過労自殺", "労災認定",
        "団体交渉", "不当労働行為", "組合潰し",
    ],
    "情報セキュリティ・個人情報": [
        "情報漏洩", "漏洩", "個人情報流出", "データ流出",
        "不正アクセス", "サイバー攻撃", "ハッキング",
        "個人情報保護法違反", "機密漏洩", "内部情報漏洩",
        "USBメモリ紛失", "データ持ち出し",
        "ランサムウェア", "マルウェア", "フィッシング",
        "情報窃取", "産業スパイ", "営業秘密侵害",
        "不正競争防止法違反", "著作権侵害", "特許侵害",
        "商標権侵害", "知的財産侵害", "海賊版", "模倣品",
        "プライバシー侵害", "盗撮", "盗聴", "GPS追跡",
    ],
    "不祥事・社会問題": [
        "不祥事", "スキャンダル", "事件", "疑惑", "疑い",
        "隠蔽", "口止め", "内部告発", "公益通報",
        "迷惑行為", "被害", "トラブル", "紛争",
        "ブラック企業", "ブラック", "悪質", "悪徳",
        "苦情", "クレーム", "炎上", "問題発覚",
        "リコール", "欠陥", "品質偽装", "データ偽装",
        "検査不正", "品質不正", "製品事故", "食品偽装",
        "産地偽装", "賞味期限改ざん", "異物混入",
        "やらせ", "ステマ", "サクラ", "口コミ偽装",
        "風評", "告発", "週刊誌", "報道",
    ],
    "思想・過激活動": [
        "右翼", "左翼", "過激派", "テロ", "テロリスト",
        "カルト", "宗教トラブル", "新興宗教", "洗脳",
        "過激思想", "差別", "ヘイト", "ヘイトスピーチ",
        "人種差別", "民族差別", "排外主義", "国粋主義",
        "革命", "武装", "爆破予告", "脅迫状",
        "街宣活動", "抗議活動", "座り込み", "妨害活動",
        "統一教会", "オウム", "旧統一教会",
    ],
    "コンプライアンス・ガバナンス": [
        "贈収賄", "接待漬け", "癒着", "利益供与",
        "利益相反", "コンプライアンス違反", "内規違反",
        "懲戒処分", "懲戒解雇", "諭旨解雇", "出勤停止",
        "減給", "戒告", "けん責", "解任", "更迭",
        "引責辞任", "経歴詐称", "学歴詐称", "職歴詐称",
        "資格詐称", "年齢詐称", "身分詐称",
        "守秘義務違反", "競業避止義務違反", "忠実義務違反",
        "善管注意義務違反", "内部統制不備", "ガバナンス不全",
        "取締役責任", "株主代表訴訟", "第三者委員会",
        "不正調査", "特別調査", "外部調査", "監査法人交代",
    ],
    "国際・制裁関連": [
        "制裁", "経済制裁", "資産凍結", "渡航禁止",
        "輸出規制", "外為法違反", "安全保障貿易管理",
        "キャッチオール規制", "不正輸出", "迂回輸出",
        "OFAC", "SDNリスト", "ブラックリスト",
        "腐敗防止法", "FCPA", "英国贈収賄防止法",
        "国際手配", "INTERPOL", "逃亡", "国外逃亡",
        "不法入国", "不法就労", "入管法違反", "偽装結婚",
    ],
}


def get_all_keywords():
    keywords = []
    for words in NEGATIVE_KEYWORDS.values():
        keywords.extend(words)
    return keywords


def build_or_queries(name, keywords, max_per_query=10):
    queries = []
    for i in range(0, len(keywords), max_per_query):
        chunk = keywords[i:i + max_per_query]
        or_part = " OR ".join(chunk)
        query = f'"{name}" ({or_part})'
        queries.append((query, chunk))
    return queries


def check_person(name, progress_callback=None, num_results=10, pause_sec=3):
    keywords = get_all_keywords()
    queries = build_or_queries(name, keywords)
    results = []
    seen_urls = set()

    for idx, (query, keyword_chunk) in enumerate(queries):
        if progress_callback:
            progress_callback(idx, len(queries), keyword_chunk)

        try:
            search_results = list(search(query, num_results=num_results, lang="ja"))
            for url in search_results:
                if url not in seen_urls:
                    seen_urls.add(url)
                    results.append({
                        "名前": name,
                        "検索クエリ": query,
                        "URL": url,
                    })
        except Exception as e:
            results.append({
                "名前": name,
                "検索クエリ": query,
                "URL": f"[エラー] {e}",
            })

        time.sleep(pause_sec)

    return results


# --- ページ設定 ---
st.set_page_config(
    page_title="コンプライアンスチェック",
    page_icon="🔍",
    layout="wide",
)

# --- カスタムCSS ---
st.markdown("""
<style>
    /* ヘッダー */
    .main-header {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 10px 0 20px 0;
        border-bottom: 3px solid #1B3A6B;
        margin-bottom: 30px;
    }
    .main-header img {
        width: 70px;
        height: auto;
    }
    .main-header-text h1 {
        margin: 0;
        color: #1B3A6B;
        font-size: 1.8rem;
    }
    .main-header-text p {
        margin: 0;
        color: #666;
        font-size: 0.95rem;
    }

    /* セクションカード */
    .section-card {
        background: #f8fafc;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    .section-title {
        color: #1B3A6B;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* 結果カード */
    .result-safe {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
    }
    .result-warning {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
    }
    .result-danger {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
    }
    .result-name {
        font-size: 1.1rem;
        font-weight: 700;
    }
    .result-count {
        font-size: 0.9rem;
        color: #666;
    }

    /* サイドバー */
    [data-testid="stSidebar"] {
        background: #f1f5f9;
    }
    .keyword-badge {
        display: inline-block;
        background: #e2e8f0;
        color: #334155;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 2px;
    }
    .keyword-count-total {
        background: #1B3A6B;
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        text-align: center;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 16px;
    }

    /* ボタン */
    .stButton > button[kind="primary"] {
        background: #1B3A6B;
        border: none;
        font-size: 1.1rem;
        padding: 0.6rem 2rem;
    }
    .stButton > button[kind="primary"]:hover {
        background: #2a5298;
    }

    /* フッター */
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        padding: 30px 0 10px 0;
        border-top: 1px solid #e2e8f0;
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)

# --- サイドバー ---
with st.sidebar:
    st.image("logo.jpg", width=120)
    st.markdown("---")
    st.markdown("#### ネガティブワード一覧")

    for category, words in NEGATIVE_KEYWORDS.items():
        with st.expander(f"{category}（{len(words)}語）"):
            badges = "".join([f'<span class="keyword-badge">{w}</span>' for w in words])
            st.markdown(badges, unsafe_allow_html=True)

    total = len(get_all_keywords())
    st.markdown(f'<div class="keyword-count-total">検索ワード合計: {total}語</div>', unsafe_allow_html=True)

# --- メインヘッダー ---
col_logo, col_text = st.columns([1, 8])
with col_logo:
    st.image("logo.jpg", width=70)
with col_text:
    st.markdown("""
    <div>
        <h1 style="color: #1B3A6B; margin: 0; font-size: 1.8rem;">コンプライアンスチェック</h1>
        <p style="color: #666; margin: 0;">個人名を入力してネガティブワード検索を自動実行します</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="border-bottom: 3px solid #1B3A6B; margin-bottom: 30px;"></div>', unsafe_allow_html=True)

# --- 名前入力 ---
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📝 名前を入力</div>', unsafe_allow_html=True)

input_method = st.radio("入力方法", ["直接入力", "CSVアップロード"], horizontal=True, label_visibility="collapsed")

names = []

if input_method == "直接入力":
    name_input = st.text_area(
        "名前を1行に1人ずつ入力してください",
        height=120,
        placeholder="山田太郎\n佐藤花子\n田中一郎",
    )
    names = [n.strip() for n in name_input.strip().split("\n") if n.strip()]
else:
    uploaded_file = st.file_uploader("CSVファイルをアップロード（1列目が名前）", type=["csv", "txt"])
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        for row in reader:
            if row and row[0].strip():
                name = row[0].strip()
                if name not in ("名前", "氏名", "name", "Name"):
                    names.append(name)

if names:
    st.info(f"対象者: **{len(names)}名** — {', '.join(names)}")

st.markdown('</div>', unsafe_allow_html=True)

# --- チェック実行 ---
st.markdown("")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_button = st.button("🔍 チェック開始", type="primary", disabled=len(names) == 0, use_container_width=True)

if run_button and names:
    all_results = []

    overall_progress = st.progress(0, text="準備中...")
    status_area = st.empty()

    for i, name in enumerate(names):
        status_area.markdown(f"**[{i + 1}/{len(names)}] {name}** を検索中...")

        def progress_callback(idx, total, keywords):
            label = " / ".join(keywords[:3]) + " ..."
            overall_pct = (i * total + idx) / (len(names) * total)
            overall_progress.progress(overall_pct, text=f"{name}: {label}")

        results = check_person(name, progress_callback=progress_callback)
        all_results.extend(results)

        overall_progress.progress((i + 1) / len(names), text=f"{name}: 完了 → {len(results)}件")

    overall_progress.progress(1.0, text="チェック完了")
    status_area.empty()

    # --- 結果表示 ---
    st.markdown('<div style="border-bottom: 3px solid #1B3A6B; margin: 30px 0 20px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 チェック結果</div>', unsafe_allow_html=True)

    for name in names:
        person_results = [r for r in all_results if r["名前"] == name and not r["URL"].startswith("[エラー]")]
        count = len(person_results)

        if count == 0:
            st.markdown(f"""
            <div class="result-safe">
                <span class="result-name">✅ {name}</span><br>
                <span class="result-count">ヒットなし — 問題は確認されませんでした</span>
            </div>
            """, unsafe_allow_html=True)
        elif count <= 5:
            st.markdown(f"""
            <div class="result-warning">
                <span class="result-name">⚠️ {name}</span><br>
                <span class="result-count">{count}件ヒット — 内容を確認してください</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-danger">
                <span class="result-name">🚨 {name}</span><br>
                <span class="result-count">{count}件ヒット — 要注意</span>
            </div>
            """, unsafe_allow_html=True)

        if person_results:
            with st.expander(f"詳細を表示（{count}件）"):
                for r in person_results:
                    st.markdown(f"- [{r['URL']}]({r['URL']})")

        error_results = [r for r in all_results if r["名前"] == name and r["URL"].startswith("[エラー]")]
        if error_results:
            with st.expander(f"⚠️ エラー（{len(error_results)}件）"):
                for r in error_results:
                    st.warning(r["URL"])

elif not names and run_button:
    st.warning("名前を入力してください")

# --- フッター ---
st.markdown("""
<div class="footer">
    ※ 本ツールはGoogle検索ベースの簡易チェックです。検索結果は参考情報としてご活用ください。<br>
    ヒット＝リスク確定ではありません。必ず内容を確認のうえ判断してください。
</div>
""", unsafe_allow_html=True)
