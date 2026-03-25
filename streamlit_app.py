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
        "組織犯罪", "マフィア", "闇社会",
    ],
    "刑事手続き": [
        "逮捕", "送検", "起訴", "容疑", "摘発", "検挙", "捜査",
        "指名手配", "釈放", "実刑", "有罪", "罰金", "懲役",
        "禁固", "書類送検", "略式起訴", "不起訴", "再逮捕",
        "取り調べ", "家宅捜索", "強制捜査", "任意同行",
        "公判", "判決", "求刑", "控訴", "上告",
    ],
    "暴力・身体犯罪": [
        "暴行", "傷害", "殺人", "恐喝", "脅迫", "監禁",
        "誘拐", "強盗", "襲撃", "DV", "ストーカー",
        "器物損壊", "放火", "未遂",
    ],
    "経済犯罪": [
        "詐欺", "横領", "着服", "窃盗", "収賄", "贈賄",
        "背任", "業務上横領", "特別背任", "架空請求",
        "振り込め詐欺", "投資詐欺", "マネーロンダリング",
        "資金洗浄", "闇金", "高利貸し", "出資法違反",
        "金融商品取引法違反", "不正送金", "持ち逃げ",
    ],
    "薬物犯罪": [
        "薬物", "覚醒剤", "大麻", "麻薬", "覚せい剤",
        "コカイン", "ヘロイン", "MDMA", "危険ドラッグ",
        "薬物所持", "薬物使用", "密売", "密輸",
    ],
    "財務・税務不正": [
        "脱税", "申告漏れ", "所得隠し", "粉飾決算", "粉飾",
        "架空取引", "循環取引", "不正会計", "簿外債務",
        "インサイダー", "インサイダー取引", "相場操縦",
        "有価証券報告書虚偽記載", "課徴金", "重加算税",
        "税務調査", "査察", "国税局",
    ],
    "法令違反・行政": [
        "違法", "違反", "不正", "偽装", "捏造", "改ざん",
        "行政処分", "行政指導", "業務停止", "業務改善命令",
        "営業停止", "免許取消", "許可取消", "是正勧告",
        "措置命令", "排除措置命令", "独占禁止法", "談合",
        "カルテル", "入札妨害", "不正入札", "下請法違反",
    ],
    "訴訟・紛争": [
        "告訴", "告発", "訴訟", "損害賠償", "民事訴訟",
        "刑事告訴", "集団訴訟", "和解", "示談", "調停",
        "仮処分", "差押", "強制執行", "破産", "倒産",
        "民事再生", "会社更生", "債務不履行", "不渡り",
    ],
    "ハラスメント・労務": [
        "パワハラ", "セクハラ", "モラハラ", "マタハラ",
        "ハラスメント", "いじめ", "嫌がらせ", "過労死",
        "過労", "長時間労働", "残業代未払い", "賃金未払い",
        "不当解雇", "労基法違反", "労働基準法違反",
        "安全配慮義務違反", "労災隠し", "偽装請負",
    ],
    "情報セキュリティ": [
        "情報漏洩", "漏洩", "個人情報流出", "データ流出",
        "不正アクセス", "サイバー攻撃", "ハッキング",
        "個人情報保護法違反", "機密漏洩", "内部情報漏洩",
        "USBメモリ紛失", "データ持ち出し",
    ],
    "不祥事・社会問題": [
        "不祥事", "スキャンダル", "事件", "疑惑", "疑い",
        "隠蔽", "口止め", "内部告発", "公益通報",
        "迷惑行為", "被害", "トラブル", "紛争",
        "ブラック企業", "ブラック", "悪質", "悪徳",
        "苦情", "クレーム", "炎上", "問題発覚",
    ],
    "思想・過激活動": [
        "右翼", "左翼", "過激派", "テロ", "テロリスト",
        "カルト", "宗教トラブル", "新興宗教", "洗脳",
        "過激思想", "差別", "ヘイト",
    ],
    "その他コンプライアンス": [
        "贈収賄", "接待漬け", "談合", "癒着", "利益供与",
        "利益相反", "コンプライアンス違反", "内規違反",
        "懲戒処分", "懲戒解雇", "諭旨解雇", "出勤停止",
        "減給", "戒告", "けん責", "解任", "更迭",
        "引責辞任", "経歴詐称", "学歴詐称",
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


# --- UI ---

st.set_page_config(page_title="コンプライアンスチェック", page_icon="🔍", layout="wide")
st.title("🔍 コンプライアンスチェック")
st.caption("名前を入力してネガティブワード検索を自動実行します")

# サイドバー: ネガティブワード一覧表示
with st.sidebar:
    st.header("ネガティブワード一覧")
    for category, words in NEGATIVE_KEYWORDS.items():
        with st.expander(f"{category}（{len(words)}語）"):
            st.write("、".join(words))
    st.divider()
    st.caption(f"合計: **{len(get_all_keywords())}語**")

# メインエリア: 名前入力
st.subheader("① 名前を入力")
input_method = st.radio("入力方法", ["直接入力", "CSVアップロード"], horizontal=True)

names = []

if input_method == "直接入力":
    name_input = st.text_area(
        "名前を1行に1人ずつ入力してください",
        height=150,
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

# 実行
st.subheader("② チェック実行")

if st.button("🔍 チェック開始", type="primary", disabled=len(names) == 0):
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

    overall_progress.progress(1.0, text="完了！")
    status_area.empty()

    # --- 結果表示 ---
    st.subheader("③ 結果")

    # サマリー
    for name in names:
        count = sum(1 for r in all_results if r["名前"] == name and not r["URL"].startswith("[エラー]"))
        if count == 0:
            st.success(f"✅ **{name}**: ヒットなし — 問題なし")
        elif count <= 5:
            st.warning(f"⚠️ **{name}**: {count}件ヒット — 内容を確認してください")
        else:
            st.error(f"🚨 **{name}**: {count}件ヒット — 要注意")

    # 詳細
    if all_results:
        st.divider()
        for name in names:
            person_results = [r for r in all_results if r["名前"] == name and not r["URL"].startswith("[エラー]")]
            error_results = [r for r in all_results if r["名前"] == name and r["URL"].startswith("[エラー]")]

            if person_results:
                with st.expander(f"📋 {name} — 詳細（{len(person_results)}件）", expanded=True):
                    for r in person_results:
                        st.markdown(f"- [{r['URL']}]({r['URL']})")
                    if error_results:
                        for r in error_results:
                            st.warning(r["URL"])
            elif error_results:
                with st.expander(f"⚠️ {name} — エラーあり"):
                    for r in error_results:
                        st.warning(r["URL"])
    else:
        st.balloons()
        st.success("🎉 全員ネガティブ情報なし！")

elif len(names) == 0:
    st.warning("名前を入力してください")
