import json
import re

with open('智能体_创建.apifox-cli.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== API Fox CLI 文件结构分析 ===')
print(f"版本: {data.get('apifoxCli', 'unknown')}")
print(f"顶层 item 数量: {len(data.get('item', []))}")

# 递归遍历所有 items
def analyze_item(item, depth=0):
    indent = "  " * depth
    name = item.get('name', 'N/A')
    item_id = item.get('id', 'N/A')[:8]
    
    if 'request' in item:
        # 这是一个请求
        req = item['request']
        method = req.get('method', 'N/A')
        url = req.get('baseUrl', '') + '/' + '/'.join(req.get('url', {}).get('path', []))
        print(f"{indent}[请求] {name} | {method} | {url[:60]}...")
        
        # 检查变量提取
        events = item.get('event', [])
        for event in events:
            if event.get('listen') == 'test':
                script_lines = event.get('script', {}).get('exec', [])
                script = '\n'.join(script_lines)
                
                # 提取 JSONPath 表达式
                jsonpath_matches = re.findall(r'`([^`]+\$\.[^`]+)`', script)
                if jsonpath_matches:
                    print(f"{indent}  -> 变量提取:")
                    for match in jsonpath_matches:
                        print(f"{indent}     - {match}")
                
                # 提取 pm.variables.set
                var_matches = re.findall(r"pm\.variables\.set\(['\"]([^'\"]+)['\"]", script)
                if var_matches:
                    print(f"{indent}  -> 设置变量: {', '.join(var_matches)}")
    else:
        # 这是一个文件夹/分组
        print(f"{indent}[文件夹] {name}")
        sub_items = item.get('item', [])
        if sub_items:
            print(f"{indent}  包含 {len(sub_items)} 个子项")
            for sub in sub_items:
                analyze_item(sub, depth + 1)

# 开始分析
for item in data.get('item', []):
    analyze_item(item)

print('\n=== 变量引用分析 ===')
# 查找所有 {{variable}} 引用
def find_variables(obj, path=""):
    variables = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                matches = re.findall(r'\{\{([^}]+)\}\}', v)
                variables.update(matches)
            else:
                variables.update(find_variables(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            variables.update(find_variables(v, f"{path}[{i}]"))
    return variables

all_vars = find_variables(data)
print(f"发现 {len(all_vars)} 个变量引用:")
for v in sorted(all_vars):
    print(f"  - {{{{{v}}}}}")
