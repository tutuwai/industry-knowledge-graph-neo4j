import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 指定下载文件夹路径
download_dir = r"C:\Users\bug\Desktop\毕设\系统\数据\数据集处理\data\专利全文"  # 修改为您的目标下载路径

# 配置Chrome选项
chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,  # 不提示下载对话框
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True  # 自动打开PDF文件，不在浏览器中预览
}
chrome_options.add_experimental_option("prefs", prefs)

# 指定ChromeDriver路径
chrome_driver_path = r"E:\GoogleChrome\chromedriver.exe"

# 启动带有特殊配置的Selenium WebDriver
driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)


def download_patent(publication_number, index, total):
    print(f"正在下载第 {index + 1} / {total} 个专利: {publication_number}")
    attempts = 0
    max_attempts = 1  # 最大重试次数
    while attempts < max_attempts:
        try:
            # 打开谷歌专利的网页
            driver.get(f'https://patents.google.com/patent/{publication_number}/zh')

            # 等待“下载PDF”按钮出现，并点击
            download_button = WebDriverWait(driver, 20).until(  # 增加等待时间
                EC.element_to_be_clickable((By.XPATH, '//*[@id="wrapper"]/div[1]/div[2]/section/header/div/a'))
            )
            download_button.click()

            # 增加等待时间，以确保文件下载
            time.sleep(1)

            print(f"专利 {publication_number} 下载完成。")
            break  # 成功下载后退出循环

        except Exception as e:
            attempts += 1
            print(f"下载专利 {publication_number} 时出错: {e}，尝试重试...（{attempts}/{max_attempts}）")
            time.sleep(1)  # 等待一段时间后重试

    if attempts == max_attempts:
        print(f"专利 {publication_number} 重试 {max_attempts} 次后仍然失败，跳过该专利。")



# 读取CSV文件中的专利公开号
patent_df = pd.read_csv('data/实体-专利.csv')
publication_numbers = patent_df['公开号'].tolist()

# 对每个公开号进行处理
# for index, publication_number in enumerate(publication_numbers):
#     download_patent(publication_number, index, len(publication_numbers))
# 对每个公开号进行处理，从第3108个开始
for index, publication_number in enumerate(publication_numbers[4120:], start=4120):
    download_patent(publication_number, index, len(publication_numbers))

# 完成后关闭浏览器
driver.quit()

print("所有专利下载完成。")

##3107 / 5803