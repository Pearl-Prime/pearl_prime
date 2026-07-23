#!/usr/bin/env python3
"""Frozen Simplified-only charset for zh-TW contamination detection.

WHY A FROZEN TABLE (and not a live OpenCC call)
-----------------------------------------------
The detection rule is the one calibrated by the zh-TW lanes and documented in
`artifacts/qa/zh_tw_scope_audit_20260715/README.md`:

    A CJK char is Simplified-only IFF BOTH:
      1. OpenCC `s2t` changes it, AND
      2. Big5 (Taiwan's charset) cannot encode it.

Condition (1) alone is WRONG: it false-flags 台/吃/游/群/床 — correct, ubiquitous
Taiwan usage — across 1,651 legitimate files. Condition (2) separates the cases.

That rule is a pure function of Unicode, so its output over the CJK Unified
Ideographs block is a FIXED, FINITE set. Freezing it here buys three things a
runtime OpenCC dependency cannot:

  * **CI cannot redden on a dependency.** No `pip install opencc` step to fail,
    no version skew silently changing the verdict under a gate that blocks merges.
  * **Determinism.** An OpenCC upgrade cannot reclassify a char and turn a green
    PR red without a reviewed diff to this file.
  * **Speed.** Set membership, not a per-char conversion call.

REGENERATION (do NOT hand-edit the tables below)
------------------------------------------------
    python3 scripts/ci/zh_tw_simplified_charset.py --regenerate   # needs opencc

That prints a refreshed module body and self-checks the calibration set. Any
change to these tables must land as a reviewed diff with the calibration intact.

Calibration (asserted by tests/test_zh_tw_simplified_contamination.py):
    NEVER flagged (legitimate Taiwan usage): 台 吃 游 群 床
    ALWAYS flagged (true Simplified):        学 说 这 个 财 双 变 录 来 续

KNOWN FALSE NEGATIVE (accepted, by design)
------------------------------------------
Rare Simplified forms that happen to sit inside Big5 (e.g. 极) are NOT flagged.
The rule is tuned for PRECISION: a false positive would reject correct
Traditional prose and train people to bypass the gate. Under-reporting is the
safe direction for a blocking gate.
"""
from __future__ import annotations

# Chars where s2t changes them AND Big5 cannot encode them -> Simplified-only.
SIMPLIFIED_ONLY_CHARS = frozenset(
    "专业丛东丝丢两严丧个临为丽举义乌乐乔习乡书买乱争亏亘亚产亩亲亵亸亿仅从仑仓仪们众会伛伞伟传伡伣伤"
    "伥伦伧伪伫佥侠侣侥侦侧侨侩侪侬侭俣俦俨俩俪俫俭债倾偬偻偾偿傤傥傧储傩兑兖兰关兴兹养兽冁内冈册写军"
    "农冯冲决况冻净凉减凑凛凤凫凭凯击凿刍刘则刚创删别刬刭刹刽刾刿剀剂剐剑剥剧劝办务劢动励劲劳势勋勚匀"
    "匦匮区医华协单卖卢卤卧卫却卺厅历厉压厌厍厐厕厢厣厦厨厩厮县叁参叆叇双发变叙叠叶号叹叽吓吕吗启吴呐"
    "呒呓呕呖呗员呙呛呜咏咙咛咝咤响哑哒哓哔哕哗哙哜哝哟唛唝唠唡唢唤啧啬啭啮啯啰啴啸喷喽喾嗫嗳嘘嘤嘱噜"
    "嚣团园囱围囵国图圆圹场块坚坛坜坝坞坟坠垄垅垆垒垦垩垫垭垯垱垲垴埘埙埚堑堕塆墙壮声壳壶壸处备够头夹"
    "夺奁奂奋奖奥妆妇妈妩妪妫姗姹娄娅娆娇娈娱娲娴婳婴婵婶媪媭嫒嫔嫱嬷孙学孪宝实宠审宪宫宽宾寝对寻导寿"
    "将尔尘尝尧尴尽层屃屉届属屡屦屿岁岂岖岗岘岚岛岽岿峃峄峡峣峤峥峦崂崃崄崭嵘嵚嵝巅巩巯币帅师帏帐帜带"
    "帧帮帱帻帼幂广庆庐庑库应庙庞废庼廪开弃弑张弥弪弯弹强归当录彟彦彨彻径徕忆忧忾态怂怃怄怅怆总怼怿恋"
    "恒恳恶恸恹恺恻恼恽悦悫悬悭悮悯惧惨惩惫惬惭惮惯愠愤愦慑慭懑懒懔戆戋戏戗战戬戯户执扩扪扫扬抚抛抟抠"
    "抡抢护报担拟拢拣拥拦拧拨择挚挛挜挝挞挟挠挡挢挣挤挥挦捝捞损捡换捣掳掴掷掸掺掼揽揾揿搀搁搂搄搅携摄"
    "摅摆摇摈摊撄撑撵撷撸撺擜擞攒敌敚敛敩数斋斓斩断无旧时旷旸昙昼昽显晋晓晔晕晖暂暅暧术杀杂权条来杨杩"
    "枞枢枣枥枧枨枪枫枭柠柽栀栅标栈栉栊栋栌栎栏树样栾桠桡桢档桤桥桦桧桨桩桪梦梼梾梿检棁棂椁椝椟椠椢椤"
    "椫椭椮楼榄榅榇榈榉榝槚槛槟槠横樯樱橥橱橹橼檩欢欤欧歼殁殇残殒殓殚殡殴毁毂毕毙毡毵毶氇氢氩氲汇汉汤"
    "汹沟没沣沤沥沦沧沨沩沪泪泶泷泸泺泻泼泽泾浃浅浆浇浈浉浊测浍济浏浐浑浒浓浔浕涚涛涝涞涟涠涡涢涣涤润"
    "涧涨涩渊渌渍渎渐渑渔渖渗温湾湿溁溃溅溆溇滗滚滞滟滠满滢滤滥滦滨滩滪潆潇潋潍潜潴澛澜濑濒灏灭灯灵灾"
    "灿炀炉炜炝点炼炽烁烂烃烛烟烦烧烨烩烫烬热焕焖焘煴爱爷牍牦牵牺犊状犷犸犹狈狝狞独狭狮狯狰狱狲猃猎猕"
    "猡猪猫猬献獭玑玙玚玛玮环现玱玺珐珑珰珲琎琏琐琼瑶瑷瑸璎瓒瓯电画畅畴疖疗疟疠疡疬疭疮疯疱疴痈痉痖痨"
    "痪痫瘅瘆瘗瘘瘪瘫瘾瘿癞癣癫皑皱皲盏盐监盖盗盘眍眦眬睁睐睑瞆瞒瞩矫矶矾矿砀码砖砗砚砜砺砻砾础硁硕硖"
    "硗硙硚硵硷碍碛碜碱礼祃祎祢祯祷祸禀禄禅秃秆积称秽秾稆税稣稳穑穞穷窃窍窎窑窜窝窥窦窭竖竞笃笋笔笕笺"
    "笼笾筚筛筜筝筹筼签筿简箓箦箧箨箩箪箫篑篓篮篯簖籁籴类籼粜粝粤粪粮糁糇糍紧絷緼縆纟纠纡红纣纤纥约级"
    "纨纩纪纫纬纭纮纯纰纱纲纳纴纵纶纷纸纹纺纻纼纽纾线绀绁绂练组绅细织终绉绊绋绌绍绎经绐绑绒结绔绕绖绗"
    "绘给绚绛络绝绞统绠绡绢绣绤绥绦继绨绩绪绫绬续绮绯绰绱绲绳维绵绶绷绸绹绺绻综绽绾绿缀缁缂缃缄缅缆缇"
    "缈缉缊缋缌缍缎缏缐缑缒缓缔缕编缗缘缙缚缛缜缝缞缟缠缡缢缣缤缥缦缧缨缩缪缫缬缭缮缯缰缱缲缳缴缵罂罗"
    "罚罢罴羁羟翘翙翚耢耧耸耻聂聋职聍联聩聪肃肠肤肾肿胀胁胆胧胨胪胫胶脉脍脏脐脑脓脔脚脱脶脸腘腭腻腼腽"
    "腾膑臜舆舣舰舱舻艰艳艺节芈芗芜芦苁苇苈苋苌苍苎苏茎茏茑茔茕荆荙荚荛荜荝荞荟荠荡荣荤荥荦荧荨荩荪荫"
    "荬荭荮药莅莱莲莳莴莶获莸莹莺莼萚萝萤营萦萧萨葱蒀蒇蒉蒋蒌蓝蓟蓠蓣蓥蓦蔷蔹蔺蔼蕰蕲蕴薮藓藴蘖虏虑虚"
    "虬虽虾虿蚀蚁蚂蚃蚬蛊蛎蛏蛮蛰蛱蛲蛳蛴蜕蜗蝇蝈蝉蝼蝾螀螨蟏衅衔补衬衮袄袅袆袜袭袯装裆裈裢裣裤裥褛褴"
    "襕见观觃规觅视觇览觉觊觋觌觍觎觏觐觑觞觯訚詟誉誊讠计订讣认讥讦讧讨让讪讫讬训议讯记讱讲讳讴讵讶讷"
    "许讹论讻讼讽设访诀证诂诃评诅识诇诈诉诊诋诌词诎诏诐译诒诓诔试诖诗诘诙诚诛诜话诞诟诠诡询诣诤该详诧"
    "诨诩诪诫诬语诮误诰诱诲诳说诵诶请诸诹诺读诼诽课诿谀谁谂调谄谅谆谇谈谉谊谋谌谍谎谏谐谑谒谓谔谕谖谗"
    "谘谙谚谛谜谝谞谟谠谡谢谣谤谥谦谧谨谩谪谫谬谭谮谯谰谱谲谳谴谵谶豮贝贞负贠贡财责贤败账货质贩贪贫贬"
    "购贮贯贰贱贲贳贴贵贶贷贸费贺贻贼贽贾贿赀赁赂赃资赅赆赇赈赉赊赋赌赍赎赏赐赑赒赓赔赕赖赗赘赙赚赛赜"
    "赝赞赟赠赡赢赣赪赵趋趱趸跃跄跞践跶跷跸跹跻踌踪踬踯蹑蹒蹰蹿躏躜躯輼车轧轨轩轪轫转轭轮软轰轱轲轳轴"
    "轵轶轷轸轹轺轻轼载轾轿辀辁辂较辄辅辆辇辈辉辊辋辌辍辎辏辐辑辒输辔辕辖辗辘辙辚辞辩辫边辽达迁过迈运"
    "还这进远违连迟迩迳迹选逊递逦逻遗遥邓邝邬邮邹邺邻郏郐郑郓郦郧郸酂酝酦酱酽酾酿醖释鉴銮錾钅钆钇针钉"
    "钊钋钌钍钎钏钐钑钒钓钔钕钖钗钘钙钚钛钜钝钞钟钠钡钢钣钤钥钦钧钨钩钪钫钬钭钮钯钰钱钲钳钴钵钶钷钸钹"
    "钺钻钼钽钾钿铀铁铂铃铄铅铆铇铈铉铊铋铌铍铎铏铐铑铒铓铔铕铖铗铘铙铚铛铜铝铞铟铠铡铢铣铤铥铦铧铨铩"
    "铪铫铬铭铮铯铰铱铲铳铴铵银铷铸铹铺铻铼铽链铿销锁锂锃锄锅锆锇锈锉锊锋锌锍锎锏锐锑锒锓锔锕锖锗锘错"
    "锚锛锜锝锞锟锠锡锢锣锤锥锦锧锨锩锪锫锬锭键锯锰锱锲锳锴锵锶锷锸锹锺锻锼锽锾锿镀镁镂镃镄镅镆镇镈镉"
    "镊镋镌镍镎镏镐镑镒镓镔镕镖镗镘镙镚镛镜镝镞镟镠镡镢镣镤镥镦镧镨镩镪镫镬镭镮镯镰镱镲镳镴镵镶长门闩"
    "闪闫闬闭问闯闰闱闲闳间闵闶闷闸闹闺闻闼闽闾闿阀阁阂阃阄阅阆阇阈阉阊阋阌阍阎阏阐阑阒阓阔阕阖阗阘阙"
    "阚阛队阳阴阵阶际陆陇陈陉陕陦陧陨险随隐隶隽难雏雠雳雾霁霡霭靓靔静靥鞑鞒鞯鞲韦韧韨韩韪韫韬韵页顶顷"
    "顸项顺须顼顽顾顿颀颁颂颃预颅领颇颈颉颊颋颌颍颎颏颐频颒颓颔颕颖颗题颙颚颛颜额颞颟颠颡颢颣颤颥颦颧"
    "风飏飐飑飒飓飔飕飖飗飘飙飚飞飨餍饣饤饥饦饧饨饩饪饫饬饭饮饯饰饱饲饳饴饵饶饷饸饹饺饻饼饽饾饿馀馁馂"
    "馃馄馅馆馇馈馉馊馋馌馍馎馏馐馑馒馓馔馕马驭驮驯驰驱驲驳驴驵驶驷驸驹驺驻驼驽驾驿骀骁骂骃骄骅骆骇骈"
    "骉骊骋验骍骎骏骐骑骒骓骔骕骖骗骘骙骚骛骜骝骞骟骠骡骢骣骤骥骦骧髅髋髌鬓鬶魇魉鱼鱽鱾鱿鲀鲁鲂鲃鲄鲅"
    "鲆鲇鲈鲉鲊鲋鲌鲍鲎鲏鲐鲑鲒鲓鲔鲕鲖鲗鲘鲙鲚鲛鲜鲝鲞鲟鲠鲡鲢鲣鲤鲥鲦鲧鲨鲩鲪鲫鲬鲭鲮鲯鲰鲱鲲鲳鲴鲵"
    "鲶鲷鲸鲹鲺鲻鲼鲽鲾鲿鳀鳁鳂鳃鳄鳅鳆鳇鳈鳉鳊鳋鳌鳍鳎鳏鳐鳑鳒鳓鳔鳕鳖鳗鳘鳙鳚鳛鳜鳝鳞鳟鳠鳡鳢鳣鳤鸟"
    "鸠鸡鸢鸣鸤鸥鸦鸧鸨鸩鸪鸫鸬鸭鸮鸯鸰鸱鸲鸳鸴鸵鸶鸷鸸鸹鸺鸻鸼鸽鸾鸿鹀鹁鹂鹃鹄鹅鹆鹇鹈鹉鹊鹋鹌鹍鹎鹏"
    "鹐鹑鹒鹓鹔鹕鹖鹗鹘鹙鹚鹛鹜鹝鹞鹟鹠鹡鹢鹣鹤鹥鹦鹧鹨鹩鹪鹫鹬鹭鹮鹯鹰鹱鹲鹳鹴鹾麦麸麹麺麽黄黉黡黩黪"
    "黾鼋鼌鼍鼹齐齑齿龀龁龂龃龄龅龆龇龈龉龊龋龌龙龚龛龟鿎鿏鿒鿔"
)

# Chars where s2t changes them but Big5 CAN encode them -> legitimate Taiwan
# usage (台/吃/游/群/床 live here). Presence of these alone is NOT contamination;
# it only marks a file as REVIEW_VARIANT_ONLY in the audit report.
BIG5_ENCODABLE_VARIANT_CHARS = frozenset(
    "万与丑丰么于云仆价优伙体余佣儿党凄准几凶划占厂厘台吁吃后吨听咨咸唇圣坏复夸宁尸岩岭岳峰帘干并庄床"
    "异征忏怀怜惊愿扑托扰挂据斗昵晒朴机杠杰极构柜栖栗气沄泞洁洒洼涂涌淀游灶炖熏瓮痒痴皂确离种秘筑篱粽"
    "网羡群肮肴胜腊腌膻苧苹范茧荐蒏蔂虫虮虱蚕蚝蜡蝎触赶跖辟适郁采里雇霉"
)


def simplified_char_counts(text: str) -> dict[str, int]:
    """Return {char: count} for every Simplified-only char in *text*."""
    counts: dict[str, int] = {}
    for ch in text:
        if ch in SIMPLIFIED_ONLY_CHARS:
            counts[ch] = counts.get(ch, 0) + 1
    return counts


def count_simplified(text: str) -> int:
    """Total number of Simplified-only characters in *text*."""
    return sum(1 for ch in text if ch in SIMPLIFIED_ONLY_CHARS)


def severity_for(n: int) -> str:
    """Severity tier for a file carrying *n* Simplified-only chars."""
    if n >= 10:
        return "WHOLE_FILE"
    if n >= 3:
        return "PARTIAL"
    return "SPOT_LEAK"


def _emit(name: str, chars: str, width: int = 48) -> str:  # pragma: no cover
    """Render a frozenset literal wrapped at *width* chars per line.

    Wrapping is REQUIRED, not cosmetic: CPython 3.9's tokenizer splits a
    multi-byte UTF-8 sequence across its internal line buffer on a single
    ~7.5 KB source line and dies with a bogus "Non-UTF-8 code" SyntaxError.
    Short lines also keep the table diff-reviewable.
    """
    import textwrap

    lines = textwrap.wrap(
        chars, width=width, break_long_words=True,
        break_on_hyphens=False, drop_whitespace=False,
    )
    body = "\n".join(f'    "{ln}"' for ln in lines)
    return f"{name} = frozenset(\n{body}\n)"


def _regenerate() -> None:  # pragma: no cover - dev tool, needs opencc
    import opencc

    conv = opencc.OpenCC("s2t")
    simp: list[str] = []
    variant: list[str] = []
    for cp in range(0x4E00, 0xA000):
        ch = chr(cp)
        if conv.convert(ch) == ch:
            continue
        try:
            ch.encode("big5")
        except (UnicodeEncodeError, LookupError):
            simp.append(ch)
        else:
            variant.append(ch)

    for ch in "台吃游群床":
        assert ch not in simp, f"calibration FAILED: {ch} must not be flagged"
    for ch in "学说这个财双变录来续":
        assert ch in simp, f"calibration FAILED: {ch} must be flagged"

    print(_emit("SIMPLIFIED_ONLY_CHARS", "".join(simp)))
    print()
    print(_emit("BIG5_ENCODABLE_VARIANT_CHARS", "".join(variant)))
    print(f"\n# simplified-only={len(simp)} variant={len(variant)}")


if __name__ == "__main__":  # pragma: no cover
    import sys

    if "--regenerate" in sys.argv:
        _regenerate()
    else:
        print(f"Simplified-only chars: {len(SIMPLIFIED_ONLY_CHARS)}")
        print(f"Big5-encodable variant chars: {len(BIG5_ENCODABLE_VARIANT_CHARS)}")
