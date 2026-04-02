# Regional Routing

How to detect which region a research topic targets and which tool cascade to use.

## Quick start

Run the detection script:
```bash
python3 skills/deep-research/scripts/detect_region.py "your research query here"
```
It returns JSON with `regions` and `cascade` fields.

---

## Region detection

Analyze the user's research query for geographic signals. The detection is
keyword-based with context awareness — a keyword alone is not enough if the
broader context is clearly global or US-focused.

### Mainland China / Hong Kong / Singapore triggers

**Geographic keywords:**
China, Chinese, mainland China, PRC, Beijing, Shanghai, Shenzhen, Guangzhou,
Hangzhou, Chengdu, Wuhan, Nanjing, Hong Kong, HK, Macau, Singapore, SG,
Pearl River Delta, Yangtze River Delta, Greater Bay Area, GBA

**Business/market keywords (when paired with a geographic signal):**
WeChat, Weibo, Xiaohongshu (RED), Douyin, TikTok (in China context), Alibaba,
Taobao, Tmall, JD.com, Pinduoduo, Baidu, Tencent, Huawei, BYD, NIO, Ant Group,
DiDi, Meituan, CATL, Shein (supply chain context), Li Auto, XPeng,
Chinese consumers, Chinese market, China regulations, PBOC, CSRC, SAFE,
renminbi, RMB, yuan, CNY, HKD, SGD, CPF, HDB, Temasek, GIC,
Grab (in SG context), Sea Limited, Shopee (in SG/SEA context)

**Cultural/social keywords:**
Golden Week (China), Spring Festival, Singles Day (11.11), 996 culture,
hukou, gaokao, guanxi, social credit, common prosperity,
Lunar New Year (in China context)

### Taiwan / Japan / Korea triggers

**Geographic keywords:**
Taiwan, Taiwanese, Taipei, Kaohsiung, Tainan, TSMC, Foxconn,
Japan, Japanese, Tokyo, Osaka, Kyoto, Nagoya, Fukuoka, Hokkaido,
Korea, Korean, South Korea, Seoul, Busan, Incheon, Jeju,
K-pop, J-pop, anime (in market research context)

**Business/market keywords:**
LINE (in Japan/Taiwan/Korea context), Rakuten, SoftBank, Sony, Toyota,
Honda, Nintendo, Panasonic, Samsung, Hyundai, Kia, SK Group, LG,
Naver, Kakao, Coupang, Mercari, Yahoo Japan, au/KDDI, NTT,
yen, JPY, won, KRW, TWD, New Taiwan Dollar,
METI, BOJ, BOK, Keidanren, chaebol, keiretsu, zaibatsu

**Cultural/social keywords:**
Golden Week (Japan), Obon, hanami, matsuri, Chuseok, Seollal,
konbini, izakaya, salaryman, hikikomori, otaku (market context),
K-beauty, K-drama, hallyu, mukbang

---

## Cascade selection logic

```
1. Parse the research query for regional keywords
2. Check for explicit region signals (strongest):
   - Proper nouns: city names, company names, regulatory bodies
   - Currency references: RMB, JPY, KRW, TWD
   - Language-specific terms: Chinese/Japanese/Korean terms in the query
3. Check for contextual signals (moderate):
   - Industry + region: "e-commerce in China", "auto market Japan"
   - Platform names: WeChat → China, LINE → Japan/Taiwan/Korea
4. If BOTH regions match (rare): use China/HK/SG cascade first, then
   Taiwan/Japan/Korea, then default
5. If NO region matches: use default cascade only
6. If AMBIGUOUS: use default cascade (don't guess)
```

### Decision examples

| Query | Region | Cascade |
|-------|--------|---------|
| "Gen Z consumer trends in Shanghai" | China | DeepSeek → default |
| "K-beauty market size and growth" | Korea | Rakuten → default |
| "Global EV market competition 2025" | None (global) | Default only |
| "TikTok marketing strategies" | None (global brand) | Default only |
| "Douyin marketing strategies" | China | DeepSeek → default |
| "LINE usage demographics Taiwan" | Taiwan | Rakuten → default |
| "Singapore fintech regulations" | Singapore | DeepSeek → default |
| "Anime market Japan vs global" | Japan | Rakuten → default |
| "Samsung vs Apple market share" | None (global) | Default only |
| "Samsung market share in Korea" | Korea | Rakuten → default |
| "Cross-border e-commerce China Japan" | Both | DeepSeek → Rakuten → default |

---

## Language handling

When a regional cascade is active, consider submitting queries in the local
language for better source coverage:

- **China/HK/SG**: Submit in Simplified Chinese (mainland) or Traditional Chinese (HK/TW)
  for local-source-heavy topics. Always translate findings to English in the report.
- **Japan**: Submit in Japanese for local market data. Translate to English in report.
- **Korea**: Submit in Korean for local market data. Translate to English in report.
- **Taiwan**: Submit in Traditional Chinese. Translate to English in report.

Only do this for topics where local-language sources would be significantly better
than English-language sources. For general business topics, English is fine.

When you translate, note it in the citation:
```
[3] (translated from Chinese) "Title of source" — https://example.cn/article
```
