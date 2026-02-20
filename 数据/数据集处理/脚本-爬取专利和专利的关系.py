import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 配置Chrome选项
chrome_options = Options()
chrome_options.add_argument('--headless')  # 无界面模式

# 指定ChromeDriver路径
chrome_driver_path = r"E:\GoogleChrome\chromedriver.exe"

# 启动Selenium WebDriver
driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)

def scrape_citations(publication_number, index, total):
    print(f"正在处理第 {index + 1} / {total} 个专利: {publication_number}")
    driver.get(f'https://patents.google.com/patent/{publication_number}/zh')

    citation_data = []

    try:
        # 确保页面已经加载了“Cited By”部分
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "citedBy"))
        )

        # 获取包含Cited By引用的容器
        cited_by_container = driver.find_element(By.XPATH, '//*[@id="citedBy"]/following-sibling::div[1]')

        # 查找所有被引用的专利链接
        citations = cited_by_container.find_elements(By.XPATH, './/state-modifier/a')
        if citations:
            print(f"找到 {len(citations)} 个被引用情况:")
        for citation in citations:
            cited_publication_number = citation.text.strip()
            print(f"  - {cited_publication_number}")
            citation_data.append((publication_number, cited_publication_number, '被引用'))
            # 实时保存到CSV文件
            save_citation_to_csv(publication_number, cited_publication_number, '被引用')

    except Exception as e:
        print(f"处理专利 {publication_number} 时出错: {e}")

    return citation_data


    return citation_data

def save_citation_to_csv(publication_number, cited_publication_number, relationship):
    # 打开文件，添加一行数据
    with open('data/关系-专利和专利-处理前.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([publication_number, cited_publication_number, relationship])

# 读取CSV文件中的专利公开号
patent_df = pd.read_csv('data/实体-专利.csv', encoding='utf-8')
publication_numbers = patent_df['公开号'].tolist()

# 检查已处理的最后一个专利
try:
    with open('data/关系-专利和专利-处理前.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        data_list = list(reader)
        last_processed = data_list[-1][0] if data_list else None
        start_index = publication_numbers.index(last_processed) + 1 if last_processed in publication_numbers else 0
except (FileNotFoundError, IndexError) as e:
    start_index = 0  # 如果文件不存在或为空，从头开始

# 对每个公开号进行处理
for index in range(start_index, len(publication_numbers)):
    publication_number = publication_numbers[index]
    scrape_citations(publication_number, index, len(publication_numbers))

# 完成后关闭浏览器
driver.quit()

print("所有专利引用关系处理完成。")
