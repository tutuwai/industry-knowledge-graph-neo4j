import csv

def process_data(input_filename, output_filename):
    # 初始化数据结构
    data = {
        '专利': [],
        '专利与发明人': [],
        '专利与ipc': [],
        '专利与申请人': [],
        '专利与代理机构': [],
        '专利与专利': []
    }

    # 读取CSV文件
    with open(input_filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 跳过标题行
        for row in reader:
            data['专利'].append(row[0])
            data['专利与发明人'].append(row[1])
            data['专利与ipc'].append(row[2])
            data['专利与申请人'].append(row[3])
            data['专利与代理机构'].append(row[4])
            data['专利与专利'].append(row[5])

    # 处理数据以符合输出格式，例如转换为字符串并添加单引号
    output_data = []
    for key, values in data.items():
        # 将每个值转换为单引号包围的字符串，整个列表包围在方括号中
        processed_values = "['" + key + "', '" + "', '".join(values) + "']"
        output_data.append(processed_values)

    # 输出到新的TXT文件或打印
    with open(output_filename, 'w', newline='') as f:
        for line in output_data:
            f.write(line + '\n')

    print("数据已经被处理并保存到", output_filename)

# 主执行逻辑
if __name__ == '__main__':
    input_file = 'data/时间数据统计.txt'  # 输入文件路径
    output_file = 'data/处理后的时间数据统计.txt'  # 输出文件路径
    process_data(input_file, output_file)
