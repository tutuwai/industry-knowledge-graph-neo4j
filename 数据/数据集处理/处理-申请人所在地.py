import pandas as pd

# 创建邮编到简化省份名的映射
zipcode_ranges = {
    '10': '北京',
    '20': '上海',
    '30': '天津',
    '40': '重庆',
    '01-02': '内蒙古',
    '03-04': '山西',
    '05-07': '河北',
    '11-12': '辽宁',
    '13': '吉林',
    '15-16': '黑龙江',
    '21-22': '江苏',
    '23-24': '安徽',
    '25-27': '山东',
    '31-32': '浙江',
    '33-34': '江西',
    '35-36': '福建',
    '41-42': '湖南',
    '43-44': '湖北',
    '45-47': '河南',
    '51-52': '广东',
    '53-54': '广西',
    '55-56': '贵州',
    '57': '海南',
    '61-64': '四川',
    '65-67': '云南',
    '71-72': '陕西',
    '73-74': '甘肃',
    '75': '宁夏',
    '81': '青海',
    '83-84': '新疆',
    '85': '西藏'
}

# 将范围转换为具体的邮编到省份的映射
zipcode_to_province = {}
for range_key, province in zipcode_ranges.items():
    if '-' in range_key:
        start, end = map(int, range_key.split('-'))
        for code in range(start, end + 1):
            zipcode_to_province[f'{code:02}'] = province
    else:
        zipcode_to_province[range_key] = province

# 读取申请人数据
applicants = pd.read_csv('data/实体-申请人.csv', header=None, names=['Name', 'PostalCode'])

# 处理邮编：提取前两位并匹配省份
def extract_province(postal_code):
    # 将邮编转换为字符串，处理可能的浮点表示
    postal_code = str(postal_code).split('.')[0].zfill(6)[:2]
    return zipcode_to_province.get(postal_code)

applicants['Province'] = applicants['PostalCode'].apply(extract_province)

# 查看结果
print(applicants)

# 保存结果
applicants.to_csv('data/实体-申请人-带省份.csv', index=False)
