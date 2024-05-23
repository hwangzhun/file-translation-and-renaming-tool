import os
import requests
import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import concurrent.futures
import time

# 翻译函数
def translate_text(text, target_language, api_key, proxy):
    url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'q': text,
        'target': target_language,
        'format': 'text'
    }
    proxies = {
        'http': proxy,
        'https': proxy
    }
    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    
    if response.status_code == 200:
        return response.json()['data']['translations'][0]['translatedText']
    else:
        print(f"翻译请求失败: {response.status_code}, {response.text}")
        return text

# 获取目录下所有文件名
def get_filenames_in_directory(directory):
    filenames = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            filenames.append(filename)
    return filenames

# 翻译并重命名文件
def translate_and_rename_file(filename, target_language, directory_path, api_key, proxy, results):
    try:
        name, extension = os.path.splitext(filename)
        translated_name = translate_text(name, target_language, api_key, proxy)
        new_filename = translated_name + extension
        os.rename(os.path.join(directory_path, filename), os.path.join(directory_path, new_filename))
        results['success'] += 1
        print(f"文件 {filename} 重命名为 {new_filename}")
    except Exception as e:
        results['failed'] += 1
        print(f"文件 {filename} 重命名失败: {e}")

# UI功能实现
class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件翻译重命名工具")

        # 选择目录按钮
        self.directory_label = tk.Label(root, text="选择目录:")
        self.directory_label.grid(row=0, column=0, padx=10, pady=5)

        self.directory_path = tk.StringVar()
        self.directory_entry = tk.Entry(root, textvariable=self.directory_path, width=50)
        self.directory_entry.grid(row=0, column=1, padx=10, pady=5)

        self.directory_button = tk.Button(root, text="浏览", command=self.browse_directory)
        self.directory_button.grid(row=0, column=2, padx=10, pady=5)

        # 选择语言下拉选项
        self.language_label = tk.Label(root, text="选择语言:")
        self.language_label.grid(row=1, column=0, padx=10, pady=5)

        self.languages = {
            "中文": "zh-CN",
            "英文": "en",
            "日语": "ja",
            "韩语": "ko",
            "法语": "fr"
        }
        self.selected_language = tk.StringVar()
        self.language_combobox = ttk.Combobox(root, textvariable=self.selected_language, values=list(self.languages.keys()))
        self.language_combobox.grid(row=1, column=1, padx=10, pady=5)

        # 输入API Key
        self.api_key_label = tk.Label(root, text="API Key:")
        self.api_key_label.grid(row=2, column=0, padx=10, pady=5)

        self.api_key_entry = tk.Entry(root, width=50)
        self.api_key_entry.grid(row=2, column=1, padx=10, pady=5)

        # 设置代理输入框
        self.proxy_label = tk.Label(root, text="设置代理 (可选):")
        self.proxy_label.grid(row=3, column=0, padx=10, pady=5)

        self.proxy_entry = tk.Entry(root, width=50)
        self.proxy_entry.grid(row=3, column=1, padx=10, pady=5)

        # 显示结果框
        self.result_text = tk.Text(root, height=10, width=70)
        self.result_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        # 开始翻译按钮
        self.translate_button = tk.Button(root, text="开始翻译", command=self.start_translation)
        self.translate_button.grid(row=4, column=1, padx=10, pady=20)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        self.directory_path.set(directory)
    
    def start_translation(self):
        directory_path = self.directory_path.get()
        target_language = self.languages.get(self.selected_language.get())
        api_key = self.api_key_entry.get()
        proxy = self.proxy_entry.get()

        if directory_path and target_language and api_key:
            filenames = get_filenames_in_directory(directory_path)
            total_files = len(filenames)
            results = {'success': 0, 'failed': 0}

            start_time = time.time()

            # 使用并发处理翻译并重命名文件
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(translate_and_rename_file, filename, target_language, directory_path, api_key, proxy, results) for filename in filenames]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"处理文件时出错: {e}")

            end_time = time.time()
            elapsed_time = end_time - start_time

            # 显示结果
            result_message = f"总文件数: {total_files}\n成功翻译: {results['success']}\n失败翻译: {results['failed']}\n耗时: {elapsed_time:.2f} 秒"
            self.result_text.insert(tk.END, result_message)

            # 确保翻译完成后打开用户选择的目录（Windows）
            subprocess.Popen(["explorer", os.path.realpath(directory_path)])
        else:
            self.result_text.insert(tk.END, "请填写所有必需的字段\n")

# 创建主窗口
root = tk.Tk()
app = TranslationApp(root)
root.mainloop()
