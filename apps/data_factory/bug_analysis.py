# -*- coding: utf-8 -*-
"""
Bug分析核心逻辑 V2
重构要点:
1. 安全修复: 边界守卫、精确异常
2. 性能优化: 预构建模块索引、合并遍历、预编译正则
3. 函数拆分: ~300行单函数 → 9个职责清晰的子函数
4. 代码质量: 扁平化嵌套、字典映射替代if/elif链、集合推导式
"""
import re
import json
import logging
from collections import Counter, defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================
# 常量与配置
# ============================================================

# MODULE_MAP 已移除 - 模块判断完全基于 Bug 标签自然汇总，无预设映射

DEFECT_KEYWORDS = {
    'UI显示': {'words': {'显示不全': 3, '样式': 3, '排版': 3, '对齐': 3, '颜色': 3, '字体': 3,
                          '布局': 3, '图标': 3, '超出': 3, '溢出': 3, '遮挡': 3, '重叠': 3,
                          '空白': 3, '不一致': 3, '样式问题': 3, '展示样式': 3, '显示为空': 3,
                          '显示异常': 3, '截断': 3, '间距': 3, '换行': 3, '文字超出': 3,
                          '位置异常': 3, '缩放': 3, '滚动条': 3, '光标定位': 3, '渲染': 3,
                          '显示': 2, '展示': 2, '展示很多空白': 3}},
    '功能逻辑': {'words': {'无法': 2, '不能': 2, '不响应': 2, '未更新': 2, '失败': 2, '未生成': 2,
                           '校验不通过': 2, '冲突': 2, '报错': 2, '无响应': 2, '未展示': 2,
                           '未显示': 2, '没有': 2, '不触发': 2, '无效': 2, '失效': 2, '丢失': 2,
                           '不生效': 2, '未生效': 2, '不执行': 2, '功能': 2}},
    '数据内容': {'words': {'英文': 2, '图片失败': 2, '为空': 2, '错误原因': 2, '乱码': 2, '缺失': 2,
                           '数据': 2, '统计': 2, '计算错误': 2, '数据不一致': 2, '数据异常': 2,
                           '有误': 2, '不准确': 2, '不正确': 2, '数量不对': 2, '多出': 2,
                           '超出限制': 2, '字数': 2, '内容': 2, '空数据': 2}},
    '交互操作': {'words': {'手势': 2, '切换要素': 2, '下拉': 2, '筛选组件': 2, '滑动': 2, '拖拽': 2,
                           '键盘遮挡': 2, '输入框': 2, '光标': 2, '选中': 2, '切换': 2, '折叠': 2,
                           '展开': 2, '滚动': 2, '拖动': 2, '点击无响应': 2, '交互': 2, '操作': 2}},
    '性能稳定': {'words': {'504': 2, '超时': 2, '白屏': 2, '偶现': 2, '一直': 2, '卡顿': 2,
                           '闪现': 2, '崩溃': 2, '死循环': 2, '闪退': 2, '频繁': 2, '频发': 2,
                           '较长时间': 2, '加载慢': 2, '响应慢': 2, '内存': 2}},
    '跨端兼容': {'words': {'浏览器': 2, 'Safari': 2, '华为浏览器': 2, '小米浏览器': 2,
                           'Firefox': 2, 'Chrome': 2, 'Edge': 2, '跨端': 2, '兼容': 2,
                           '微信浏览器': 2, '安卓': 2, '苹果': 2, '鸿蒙': 2, 'APP端': 2,
                           'H5端': 2, 'PC端': 2}},
}

P0_WORDS = ['白屏', '504', '崩溃', '死循环', '闪退', '数据丢失']
P1_WORDS = ['无法', '不能', '不响应', '一直', '超时', '报错', '无响应', '频发']

END_WORDS = ['PC', 'H5', 'APP', '学员端', '运营端', '鸿蒙', '安卓', '苹果',
             'Safari', '华为浏览器', '小米浏览器', 'Firefox', 'Chrome', 'Edge',
             '微信浏览器', '偶现', '二期', '一期', '优化']

CROSS_END_WORDS = ['浏览器', 'Safari', '华为', '小米', 'Firefox', 'Chrome', 'Edge',
                   '跨端', '兼容', '安卓', '苹果', '鸿蒙', 'APP端', 'H5端', 'PC端']

# 预编译正则: 关键词匹配 (性能优化: 38次 in 操作 → 1次正则扫描)
KEYWORDS_LIST = [
    '不显示', '报错', '超时', '白屏', '截断', '缺失', '样式', '布局',
    '加载', '点击', '刷新', '提交', '播放', '登录', '创建', '编辑',
    '切换', '导出', '下载', '搜索', '筛选', '兼容', '闪退', '卡顿',
    '校验', '交互', '内容', '文字', '格式', '空数据', '重叠', '遮挡',
    '异常', '错乱', '渲染', '图标', '颜色', '字体', '响应', '联动',
    '输入', '删除', '无法', '显示', '展开'
]
_KW_REGEX = re.compile('|'.join(re.escape(kw) for kw in KEYWORDS_LIST))

# 严重度原始标签映射 (扁平化 if/elif 链)
_SEVERITY_ORIG_MAP = {
    '1-致命': '1-致命', '致命': '1-致命',
    '2-严重': '2-严重', '严重': '2-严重',
    '3-一般': '3-一般', '一般': '3-一般',
    '4-轻微': '4-轻微', '轻微': '4-轻微',
}

# 时间线批量引入阈值
IMPORT_THRESHOLD = 2

# 聚集数据最少Bug数阈值
CLUSTER_MIN_BUGS = 5


# ============================================================
# 基础分类函数（保持原有逻辑 + 安全修复）
# ============================================================

def extract_tags(title):
    """从标题提取【】或[]中的标签"""
    tags = re.findall(r'【(.*?)】', title)
    if not tags:
        tags = re.findall(r'\[(.*?)\]', title)
    return tags


def classify_module(tags, title):
    """
    分类模块 - 直接返回 Bug 标签本身，不再映射到预定义模块
    核心逻辑: 基于标签自然汇总，无预设模块映射
    """
    feature_tags = [t for t in tags if t not in END_WORDS and len(t) > 1]
    if not feature_tags:
        # 无标签时，尝试从标题中提取关键词作为模块
        clean = re.sub(r'【.*?】|\[.*?\]', '', title)
        # 返回标题前10个字符作为兜底
        return clean[:10] if clean else '其他'

    # 直接返回第一个有效标签（通常是主要模块标识）
    # 这样模块分布完全基于实际标签的自然汇总
    return feature_tags[0]


def classify_defect(title, desc=''):
    """基于关键词加权评分分类缺陷类型"""
    title_text = title
    desc_text = (desc or '')[:200]

    scores = {}
    for dtype, kw_info in DEFECT_KEYWORDS.items():
        score = 0
        sorted_words = sorted(kw_info['words'].items(), key=lambda x: len(x[0]), reverse=True)
        covered_ranges = []
        for word, pts in sorted_words:
            idx = title_text.find(word)
            if idx >= 0:
                overlap = any(s <= idx < e or s < idx + len(word) <= e for s, e in covered_ranges)
                if not overlap:
                    score += pts * 3
                    covered_ranges.append((idx, idx + len(word)))
            else:
                idx = desc_text.find(word)
                if idx >= 0:
                    overlap = any(s <= idx < e or s < idx + len(word) <= e for s, e in covered_ranges)
                    if not overlap:
                        score += pts
                        covered_ranges.append((idx, idx + len(word)))
        scores[dtype] = score

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_type, best_score = sorted_scores[0]

    if best_score < 2:
        return '其他'

    if len(sorted_scores) > 1 and sorted_scores[1][1] > 0:
        gap = best_score - sorted_scores[1][1]
        if gap < 2:
            return '其他'

    return best_type


def infer_severity(title, desc='', original_sev=''):
    """推断严重度 P0/P1/P2"""
    text = title + ' ' + desc
    for w in P0_WORDS:
        if w in text:
            return 'P0'
    for w in P1_WORDS:
        if w in text:
            return 'P1'

    # 使用原始严重度映射 (替代原来的 if/elif 链)
    orig_str = str(original_sev)
    for key, label in _SEVERITY_ORIG_MAP.items():
        if key in orig_str:
            return 'P0' if label in ('1-致命',) else ('P1' if label in ('2-严重',) else 'P2')

    return 'P2'


def _normalize_original_severity(sev_value):
    """
    将原始严重度值标准化为统一标签
    替代原来内联在 analyze_bugs() 中的 if/elif 链
    """
    if not sev_value:
        return '未知'
    sev_str = str(sev_value)
    for key, label in _SEVERITY_ORIG_MAP.items():
        if key in sev_str:
            return label
    return '未知'


# ============================================================
# 预处理与索引构建
# ============================================================

def _preprocess_bugs(bugs):
    """
    预处理每条bug: 提取标签、分类模块、缺陷类型、推断严重度
    直接在原列表上修改，避免创建新列表节省内存
    """
    for b in bugs:
        b['tags'] = extract_tags(b.get('title', ''))
        b['module'] = classify_module(b['tags'], b.get('title', ''))
        b['defect_type'] = classify_defect(b.get('title', ''), b.get('desc', ''))
        b['inferred_sev'] = infer_severity(
            b.get('title', ''), b.get('desc', ''), b.get('severity', '')
        )
    return bugs


def _build_module_index(bugs):
    """
    预构建 module → bugs 索引 (性能关键优化)
    将后续 O(n*m) 的模块过滤降为 O(n+m) 构建索引 + O(1) 查找
    返回: (module_counter[Counter], module_index[defaultdict(list)])
    """
    module_index = defaultdict(list)
    module_counter = Counter()
    for b in bugs:
        mod = b.get('module')
        if mod:
            module_index[mod].append(b)
            module_counter[mod] += 1
    return module_counter, module_index


def _compute_all_modules(module_counter):
    """返回所有模块（不再限制为TOP10），所有内容都在柱状图中显示"""
    return [mod for mod, cnt in module_counter.most_common()]


def _is_online_bug(b):
    """判断是否为线上故障 Bug"""
    return '线上故障' in b.get('type', '')


def _is_reopened(b):
    """判断是否为重新打开的 Bug"""
    status = b.get('status', '')
    return '再次打开' in status or '重新打开' in status


# ============================================================
# 子函数：各维度数据计算
# ============================================================

def _compute_modules_data(module_counter, module_index, all_modules, total):
    """
    计算模块分布数据 + 特征明细数据
    所有模块都显示在柱状图中，不再有"未归类"
    """
    # modulesData: 所有模块的计数
    modules_data = {mod: module_counter[mod] for mod in all_modules if module_counter.get(mod, 0) > 0}
    # 不再计算未归类，所有内容都在柱状图中显示
    uncategorized = 0

    # featureDetailData: 每个模块下的特征标签分布
    # 直接基于标签自然汇总，无预设模块映射
    feature_counter = defaultdict(Counter)
    for mod in all_modules:
        for b in module_index.get(mod, []):
            feature_tags = [t for t in b['tags'] if t not in END_WORDS and len(t) > 1]
            if feature_tags:
                # 直接使用第一个有效标签作为特征
                matched_feature = feature_tags[0]
                feature_counter[mod][matched_feature] += 1

    feature_detail_data = []
    for mod in all_modules:
        children = [{'name': feat, 'value': count} for feat, count in feature_counter[mod].most_common()]
        if children:
            feature_detail_data.append({'name': mod, 'children': children})

    return modules_data, feature_detail_data, uncategorized


def _compute_severity_data(bugs):
    """
    计算严重度相关数据:
    - severityCrossData: 原始严重度 × 推断严重度 交叉表
    - sevData: 原始严重度分布
    - sevInfData: 推断严重度(P0/P1/P2)分布
    - statusData: 状态分布
    - priorityData: 优先级分布
    """
    sev_cross = defaultdict(lambda: defaultdict(int))
    sev_counter = Counter()
    p_counts = {'P0': 0, 'P1': 0, 'P2': 0}
    status_counter = Counter()
    priority_counter = Counter()

    for b in bugs:
        # 交叉表 (使用标准化函数替代 if/elif 链)
        orig_label = _normalize_original_severity(b.get('severity', ''))
        sev_cross[orig_label][b['inferred_sev']] += 1

        # 原始严重度分布
        if b.get('severity'):
            sev_counter[b['severity']] += 1

        # 推断严重度计数
        inf_sev = b['inferred_sev']
        if inf_sev in p_counts:
            p_counts[inf_sev] += 1

        # 状态和优先级
        if b.get('status'):
            status_counter[b['status']] += 1
        if b.get('priority'):
            priority_counter[b['priority']] += 1

    severity_cross_data = {k: dict(v) for k, v in sev_cross.items()}
    sev_inf_data = {f'推断{k}': v for k, v in p_counts.items()}

    return (
        severity_cross_data,
        dict(sev_counter),
        sev_inf_data,
        dict(status_counter),
        dict(priority_counter),
    )


def _compute_test_focus(top10, module_index):
    """
    计算每个 TOP10 模块的测试重点数据
    使用预建索引避免重复 O(n) 过滤
    """
    tf_data = {}
    for mod in top10:
        mod_bugs = module_index.get(mod, [])
        mod_total = len(mod_bugs)
        if mod_total == 0:
            continue

        dtype_counter = Counter(b['defect_type'] for b in mod_bugs)
        online_count = sum(1 for b in mod_bugs if _is_online_bug(b))
        reopened_count = sum(1 for b in mod_bugs if _is_reopened(b))

        focus_points = _build_focus_points(
            mod_total, online_count, reopened_count, dtype_counter, mod_bugs
        )

        tf_data[mod] = {
            'total': mod_total,
            'online': online_count,
            'reopened': reopened_count,
            'top_types': [[t, c] for t, c in dtype_counter.most_common(3)],
            'focus_points': focus_points,
            'dtype_dist': dict(dtype_counter),
        }

    return tf_data


def _build_focus_points(mod_total, online_count, reopened_count, dtype_counter, mod_bugs):
    """
    构建测试关注点文案列表
    扁平化: 将原来 testFocusData 中内联的复杂 if/elif 抽取为独立函数
    """
    focus_points = []

    # 线上故障关注点
    if online_count > 0:
        pct = round(online_count / mod_total * 100)
        if pct >= 10:
            focus_points.append(
                f"线上故障回归: {online_count}条(占{pct}%)线上故障，迭代后必须逐条验证线上已发生的场景不会复现"
            )
        else:
            focus_points.append(
                f"备注: 含{online_count}条(占{pct}%)线上故障(较少)，迭代时顺手覆盖即可"
            )

    # 缺陷类型专项回归
    type_focus_rules = [
        ('数据内容', f"数据完整性回归: 占比{{p}}%涉及数据截断/缺失/格式，迭代后重点验证数据展示完整性、特殊字符、空数据"),
        ('跨端兼容', f"跨端兼容回归: 占比{{p}}%涉及多端差异，迭代后重点验证PC/H5/APP三端一致性"),
        ('UI显示', f"UI渲染回归: 占比{{p}}%涉及展示/样式/截断，迭代后重点验证页面布局、文字截断、样式错乱"),
    ]

    for dtype_name, template in type_focus_rules:
        count_val = dtype_counter.get(dtype_name, 0)
        if count_val > 0:
            pct = round(count_val / mod_total * 100)
            if pct >= 10:
                focus_points.append(template.replace('{{p}}', str(pct)).format(p=pct, count=count_val))

    # 通用基础回归
    func_pct = round(dtype_counter.get('功能逻辑', 0) / mod_total * 100)
    inter_pct = round(dtype_counter.get('交互操作', 0) / mod_total * 100)
    focus_points.append(
        f"通用基础回归: 功能逻辑占{func_pct}%+交互操作占{inter_pct}%，迭代后验证核心流程不卡壳不阻塞+按钮响应/筛选联动"
    )

    # 典型Bug举例
    examples = [b['title'] for b in mod_bugs if _is_online_bug(b)][:3]
    if not examples:
        examples = [b['title'] for b in mod_bugs[:3]]
    if examples:
        focus_points.insert(-1, "典型Bug举例: " + "；".join(examples))

    return focus_points


def _compute_creator_data(bugs):
    """计算创建者-模块分布数据"""
    creator_mod = defaultdict(lambda: defaultdict(int))
    creator_online = defaultdict(int)

    for b in bugs:
        creator = b.get('creator', '')
        if creator:
            creator_mod[creator][b['module'] or '其他'] += 1
            if _is_online_bug(b):
                creator_online[creator] += 1

    result = []
    for creator in sorted(creator_mod.keys(), key=lambda c: sum(creator_mod[c].values()), reverse=True):
        total_c = sum(creator_mod[creator].values())
        online_c = creator_online.get(creator, 0)
        result.append({
            'creator': creator,
            'total': total_c,
            'online': online_c,
            'online_pct': round(online_c / total_c * 100, 1) if total_c > 0 else 0,
            'modules': dict(creator_mod[creator]),
        })

    return result


def _compute_timeline_data(bugs):
    """
    计算时间线数据 (合并原来两次遍历为一次)
    返回: (timelineCleanData, timelineData, importLabels, import_count, real_count)
    """
    # 单次遍历: 同时完成日期计数和批量检测识别
    date_counter = Counter()
    all_date_counter = Counter()
    created_datetime_list = []

    for b in bugs:
        created = b.get('created')
        if isinstance(created, datetime):
            created_datetime_list.append(created)
            date_str = created.strftime('%Y-%m-%d')
            all_date_counter[date_str] += 1

    # 批量引入检测: 同一天出现 >= IMPORT_THRESHOLD 条的视为批量引入
    time_counter = Counter(created_datetime_list)
    import_dates_set = {dt for dt, cnt in time_counter.items() if cnt >= IMPORT_THRESHOLD}

    import_dates = defaultdict(int)
    for dt in created_datetime_list:
        if dt in import_dates_set:
            import_dates[dt.strftime('%Y-%m-%d')] += 1

    # timelineCleanData: 排除批量引入后的正常散布数据
    clean_date_counter = Counter()
    for dt in created_datetime_list:
        if dt not in import_dates_set:
            clean_date_counter[dt.strftime('%Y-%m-%d')] += 1

    timeline_clean_data = dict(sorted(clean_date_counter.items()))
    timeline_data = dict(sorted(all_date_counter.items()))
    import_labels = [{'date': d, 'count': c} for d, c in sorted(import_dates.items())]
    import_count_total = sum(import_dates.values())
    real_count = sum(clean_date_counter.values())

    return timeline_clean_data, timeline_data, import_labels, import_count_total, real_count


def _compute_keyword_data(bugs):
    """
    计算关键词词频数据 (使用预编译正则优化)
    返回: (kwData, wufaDetailData)
    """
    kw_counter = Counter()
    wufa_patterns = Counter()

    for b in bugs:
        title = b.get('title', '')

        # 关键词匹配: 使用预编译正则 (性能优化)
        found_kw = _KW_REGEX.findall(title)
        for kw in found_kw:
            kw_counter[kw] += 1

        # 无法XXX 模式提取
        m = re.search(r'无法(\w{2,4})', title)
        if m:
            wufa_patterns[f"无法{m.group(1)}"] += 1

    kw_data = [[kw, cnt] for kw, cnt in kw_counter.most_common(20)]
    wufa_detail_data = dict(wufa_patterns.most_common(20))

    return kw_data, wufa_detail_data


def _compute_risk_data(bugs, p_counts):
    """
    计算风险分析数据 (扁平化: 替代三层 if/elif 嵌套)
    使用分发模式替代深层条件判断
    注意：风险类型由AI动态分析生成，此函数仅提供基础统计数据，不预设任何风险分类
    """
    # 不再预设任何风险类型，返回空的detail结构
    # AI将根据原始Bug数据进行动态风险分析
    risk_data = {
        'P0': {'total': p_counts['P0'], 'detail': {}},
        'P1': {'total': p_counts['P1'], 'detail': {}},
        'P2': {'total': p_counts['P2'], 'detail': {}},
    }

    return risk_data


def _compute_cluster_data(bugs, module_index):
    """
    计算聚集数据 + 根因数据 + 模块×类型交叉数据
    使用预建索引避免重复过滤
    """
    # 聚集数据: 所有模块的 Bug 数分布 (Top 25, 最少 CLUSTER_MIN_BUGS 条)
    all_modules = Counter(b['module'] or '其他' for b in bugs)
    cluster_data = []
    for feat, count in all_modules.most_common(25):
        if count < CLUSTER_MIN_BUGS:
            break
        mod_bugs = module_index.get(feat, []) or [b for b in bugs if (b['module'] or '其他') == feat]
        type_dist = Counter(b['defect_type'] for b in mod_bugs)
        cluster_data.append({'feature': feat, 'bug_count': count, 'type_distribution': dict(type_dist)})

    # 根因数据: 基于 clusterData 前15个模块生成根因假设字符串
    root_cause_data = []
    for item in cluster_data[:15]:
        mod = item['feature']
        mod_bugs_local = module_index.get(mod, []) or [b for b in bugs if (b['module'] or '其他') == mod]
        td = item['type_distribution']
        sorted_types = sorted(td.items(), key=lambda x: x[1], reverse=True)
        top2 = sorted_types[:2]
        cause_parts = [f"{t}({c}条)" for t, c in top2]
        cause = '+'.join(cause_parts)
        if len(top2) >= 2:
            cause += f" → {' + '.join(t + '缺陷' for t, _ in top2)}"
        root_cause_data.append({
            'module': mod,
            'count': item['bug_count'],
            'cause': cause,
            'type_distribution': td,
        })

    # 模块×类型交叉数据
    cross_type_data = {}
    for b in bugs:
        mod = b['module'] or '其他'
        wt = b.get('type', '') or '未知'
        key = f"{mod}|{wt}"
        cross_type_data[key] = cross_type_data.get(key, 0) + 1

    return cluster_data, root_cause_data, cross_type_data


def _build_metadata(bugs, xlsx_filename, uncategorized, import_count, real_count):
    """
    构建元数据信息
    使用集合推导式简化 tag 收集
    """
    total = len(bugs)

    # 集合推导式 (代码简化)
    tag_set = {tag for b in bugs for tag in b['tags']}
    creators = {b.get('creator', '') for b in bugs if b.get('creator')}
    work_types = dict(Counter(b.get('type', '') for b in bugs if b.get('type')))

    meta_data = {
        'total_bugs': total,
        'input_file': xlsx_filename,
        'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'creators': len(creators),
        'work_types': work_types,
        'tag_count': len(tag_set),
        'uncategorized': uncategorized,
        'uncategorized_pct': round(uncategorized / total * 100, 1) if total > 0 else 0,
        'import_count': import_count,
        'real_count': real_count,
    }
    return meta_data


# ============================================================
# 空结果快速返回 (安全守卫)
# ============================================================

_EMPTY_RESULT_TEMPLATE = {
    'modulesData': {},
    'featureDetailData': [],
    'severityCrossData': {},
    'testFocusData': {},
    'creatorModuleData': [],
    'timelineCleanData': {},
    'timelineData': {},
    'importLabels': [],
    'kwData': [],
    'riskData': {'P0': {'total': 0, 'detail': {}}, 'P1': {'total': 0, 'detail': {}}, 'P2': {'total': 0, 'detail': {}}},
    'clusterData': [],
    'rootCauseData': [],
    'crossTypeData': {},
    'sevData': {},
    'sevInfData': {'推断P0': 0, '推断P1': 0, '推断P2': 0},
    'statusData': {},
    'priorityData': {},
    'wufaDetailData': {},
    'metaData': {
        'total_bugs': 0, 'input_file': '', 'analysis_time': '',
        'creators': 0, 'work_types': {}, 'tag_count': 0,
        'uncategorized': 0, 'uncategorized_pct': 0,
        'import_count': 0, 'real_count': 0,
    },
}


# ============================================================
# 主入口
# ============================================================

def analyze_bugs(bugs, xlsx_filename=''):
    """
    分析 Bug 数据的主入口函数

    重构后架构:
    1. 空列表早返回 (安全守卫)
    2. 预处理 (标签提取/分类)
    3. 构建模块索引 (一次性 O(n))
    4. 分发到各子函数计算 (各子函数使用索引 O(1) 查找)
    5. 组装结果返回

    Args:
        bugs: Bug 列表, 每个元素为 dict 含 title/desc/severity/status/priority/type/creator/created 字段
        xlsx_filename: 来源文件名 (用于元数据记录)

    Returns:
        dict: 包含所有分析结果的完整字典
    """
    # 安全守卫: 空列表快速返回
    if not bugs:
        result = dict(_EMPTY_RESULT_TEMPLATE)
        result['metaData']['input_file'] = xlsx_filename
        result['metaData']['analysis_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        return result

    total = len(bugs)

    # Step 1: 预处理
    _preprocess_bugs(bugs)

    # Step 2: 构建模块索引 (性能核心: 后续所有模块查询走索引)
    module_counter, module_index = _build_module_index(bugs)
    all_modules = _compute_all_modules(module_counter)

    # Step 3: 各维度数据计算
    modules_data, feature_detail_data, uncategorized = _compute_modules_data(
        module_counter, module_index, all_modules, total
    )

    severity_cross_data, sev_data, sev_inf_data, status_data, priority_data = _compute_severity_data(bugs)

    p_counts = {'P0': sev_inf_data.get('推断P0', 0), 'P1': sev_inf_data.get('推断P1', 0), 'P2': sev_inf_data.get('推断P2', 0)}

    tf_data = _compute_test_focus(all_modules, module_index)
    creator_module_data = _compute_creator_data(bugs)
    timeline_clean_data, timeline_data, import_labels, import_count, real_count = _compute_timeline_data(bugs)
    # kw_data 不再在基础分析中计算，由 AI 增强阶段生成
    risk_data = _compute_risk_data(bugs, p_counts)
    cluster_data, root_cause_data, cross_type_data = _compute_cluster_data(bugs, module_index)
    meta_data = _build_metadata(bugs, xlsx_filename, uncategorized, import_count, real_count)

    # Step 4: 组装并返回结果 (保持原有 JSON 结构不变，确保前端兼容)
    return {
        'modulesData': modules_data,
        'featureDetailData': feature_detail_data,
        'severityCrossData': severity_cross_data,
        'testFocusData': tf_data,
        'creatorModuleData': creator_module_data,
        'timelineCleanData': timeline_clean_data,
        'timelineData': timeline_data,
        'importLabels': import_labels,
        'kwData': [],  # 关键词由 AI 增强阶段生成
        'riskData': risk_data,
        'clusterData': cluster_data,
        'rootCauseData': root_cause_data,
        'crossTypeData': cross_type_data,
        'sevData': sev_data,
        'sevInfData': sev_inf_data,
        'statusData': status_data,
        'priorityData': priority_data,
        'wufaDetailData': {},  # 无法XXX模式也由 AI 提取
        'metaData': meta_data,
    }
