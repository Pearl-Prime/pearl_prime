#!/usr/bin/env python3
"""
detect_region.py — Detect geographic region from a research query.

Usage:
    python3 detect_region.py "Gen Z consumer trends in Shanghai"

Output (JSON):
    {"regions": ["china_hk_sg"], "cascade": ["deepseek_deep", "deepseek_regular", "gemini_deep", "chatgpt_deep", "claude_deep", "chatgpt_regular"]}
"""

import json
import re
import sys

CHINA_HK_SG_KEYWORDS = [
    # Cities / regions
    r"\bchina\b", r"\bchinese\b", r"\bmainland china\b", r"\bprc\b",
    r"\bbeijing\b", r"\bshanghai\b", r"\bshenzhen\b", r"\bguangzhou\b",
    r"\bhangzhou\b", r"\bchengdu\b", r"\bwuhan\b", r"\bnanjing\b",
    r"\bhong kong\b", r"\bhk\b", r"\bmacau\b",
    r"\bsingapore\b", r"\bsg\b",
    r"\bpearl river delta\b", r"\byangtze\b", r"\bgreater bay area\b", r"\bgba\b",
    # Platforms / companies
    r"\bwechat\b", r"\bweibo\b", r"\bxiaohongshu\b", r"\bdouyin\b",
    r"\balibaba\b", r"\btaobao\b", r"\btmall\b", r"\bjd\.com\b",
    r"\bpinduoduo\b", r"\bbaidu\b", r"\btencent\b", r"\bhuawei\b",
    r"\bbyd\b", r"\bnio\b", r"\bant group\b", r"\bdidi\b", r"\bmeituan\b",
    r"\bcatl\b", r"\bli auto\b", r"\bxpeng\b",
    # Currency / regulatory
    r"\brenminbi\b", r"\brmb\b", r"\byuan\b", r"\bcny\b",
    r"\bhkd\b", r"\bsgd\b", r"\bcpf\b", r"\bhdb\b",
    r"\bpboc\b", r"\bcsrc\b", r"\bsafe\b",
    r"\btemasek\b", r"\bgic\b", r"\bgrab\b", r"\bsea limited\b",
    # Cultural
    r"\bsingles day\b", r"\b11\.11\b", r"\b996\b", r"\bhukou\b",
    r"\bgaokao\b", r"\bguanxi\b", r"\bsocial credit\b", r"\bcommon prosperity\b",
]

TAIWAN_JAPAN_KOREA_KEYWORDS = [
    # Cities / regions
    r"\btaiwan\b", r"\btaiwanese\b", r"\btaipei\b", r"\bkaohsiung\b", r"\btainan\b",
    r"\bjapan\b", r"\bjapanese\b", r"\btokyo\b", r"\bosaka\b", r"\bkyoto\b",
    r"\bnagoya\b", r"\bfukuoka\b", r"\bhokkaido\b",
    r"\bkorea\b", r"\bkorean\b", r"\bsouth korea\b", r"\bseoul\b",
    r"\bbusan\b", r"\bincheon\b", r"\bjeju\b",
    # Companies / platforms
    r"\btsmc\b", r"\bfoxconn\b",
    r"\brakuten\b", r"\bsoftbank\b", r"\bsony\b", r"\btoyota\b",
    r"\bhonda\b", r"\bnintendo\b", r"\bpanasonic\b",
    r"\bsamsung\b", r"\bhyundai\b", r"\bkia\b", r"\bsk group\b", r"\blg\b",
    r"\bnaver\b", r"\bkakao\b", r"\bcoupang\b", r"\bmercari\b",
    r"\byahoo japan\b", r"\bkddi\b", r"\bntt\b",
    # Currency
    r"\byen\b", r"\bjpy\b", r"\bwon\b", r"\bkrw\b", r"\btwd\b",
    r"\bnew taiwan dollar\b",
    # Regulatory / cultural
    r"\bmeti\b", r"\bboj\b", r"\bbok\b", r"\bkeidanren\b",
    r"\bchaebol\b", r"\bkeiretsu\b",
    r"\bk-pop\b", r"\bj-pop\b", r"\banime\b",
    r"\bk-beauty\b", r"\bk-drama\b", r"\bhallyu\b",
    r"\bgolden week\b.*japan", r"\bobon\b", r"\bhanami\b",
    r"\bchuseok\b", r"\bseollal\b",
]

DEFAULT_CASCADE = [
    "gemini_deep", "chatgpt_deep", "claude_deep", "chatgpt_regular"
]

CHINA_CASCADE = [
    "deepseek_deep", "deepseek_regular"
]

TJK_CASCADE = [
    "rakuten_deep", "rakuten_regular"
]


def detect(query: str):
    q = query.lower()
    regions = []

    china_score = sum(1 for kw in CHINA_HK_SG_KEYWORDS if re.search(kw, q))
    tjk_score = sum(1 for kw in TAIWAN_JAPAN_KOREA_KEYWORDS if re.search(kw, q))

    if china_score > 0:
        regions.append("china_hk_sg")
    if tjk_score > 0:
        regions.append("taiwan_japan_korea")

    # Build cascade
    cascade = []
    if "china_hk_sg" in regions:
        cascade.extend(CHINA_CASCADE)
    if "taiwan_japan_korea" in regions:
        cascade.extend(TJK_CASCADE)
    cascade.extend(DEFAULT_CASCADE)

    return {
        "regions": regions if regions else ["global"],
        "china_score": china_score,
        "tjk_score": tjk_score,
        "cascade": cascade,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: detect_region.py <query>", file=sys.stderr)
        sys.exit(1)
    result = detect(" ".join(sys.argv[1:]))
    print(json.dumps(result, indent=2))
