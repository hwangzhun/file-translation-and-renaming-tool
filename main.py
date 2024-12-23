import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import time
from file_processing import get_filenames_in_directory, translate_and_rename_file, retry_failed_translations

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件翻译重命名工具 v1.0.2")

        # 获取屏幕尺寸
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # 设置窗口最小尺寸
        min_width = int(screen_width * 0.3)
        min_height = int(screen_height * 0.5)
        self.root.minsize(min_width, min_height)

        # 设置窗口初始尺寸为屏幕的百分比
        init_width = int(screen_width * 0.3)
        init_height = int(screen_height * 0.5)
        self.root.geometry(f"{init_width}x{init_height}")

        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky='nsew')

        self.create_google_tab()
        self.create_baidu_tab()
        self.create_bing_tab()

        # 选择目录按钮
        self.directory_label = tk.Label(root, text="选择目录:")
        self.directory_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

        self.directory_path = tk.StringVar()
        self.directory_entry = tk.Entry(root, textvariable=self.directory_path, width=50)
        self.directory_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        self.directory_button = tk.Button(root, text="浏览", command=self.browse_directory)
        self.directory_button.grid(row=1, column=2, padx=10, pady=5, sticky='e')

        # 选择语言下拉选项
        self.language_label = tk.Label(root, text="选择语言:")
        self.language_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')

        self.languages = {
            "中文": "zh-CN",
            "英文": "en",
            "日语": "ja",
            "韩语": "ko",
            "法语": "fr"
        }
        self.selected_language = tk.StringVar()
        self.language_combobox = ttk.Combobox(root, textvariable=self.selected_language, values=list(self.languages.keys()))
        self.language_combobox.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

        # 设置代理输入框
        self.proxy_label = tk.Label(root, text="设置代理 (可选):")
        self.proxy_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')

        self.proxy_entry = tk.Entry(root, width=50)
        self.proxy_entry.grid(row=3, column=1, padx=10, pady=5, sticky='ew')

        # 显示结果框
        self.result_text = tk.Text(root, height=10)
        self.result_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        # 显示日志框和垂直滚动条
        self.log_frame = tk.Frame(root)
        self.log_frame.grid(row=7, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        self.log_text = tk.Text(self.log_frame, height=10, wrap='none')
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_scrollbar = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.log_scrollbar.set)

        # 设置日志样式
        self.log_text.tag_configure('green', foreground='green')
        self.log_text.tag_configure('red', foreground='red')
        self.log_text.tag_configure('black', foreground='black')

        # 进度条
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

        # 开始翻译按钮
        self.translate_button = tk.Button(root, text="开始翻译", command=self.start_translation)
        self.translate_button.grid(row=4, column=0, padx=10, pady=20, sticky='e')

        # 打开目录按钮
        self.open_directory_button = tk.Button(root, text="打开目录", command=self.open_directory)
        self.open_directory_button.grid(row=4, column=2, padx=10, pady=20, sticky='w')

        # 配置响应式布局
        for i in range(8):
            self.root.grid_rowconfigure(i, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def create_google_tab(self):
        self.google_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.google_frame, text="Google")

        self.google_api_key_label = tk.Label(self.google_frame, text="API Key:")
        self.google_api_key_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        self.google_api_key_entry = tk.Entry(self.google_frame, width=50)
        self.google_api_key_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

        self.google_frame.grid_columnconfigure(1, weight=1)

    def create_baidu_tab(self):
        self.baidu_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.baidu_frame, text="Baidu")

        self.baidu_appid_label = tk.Label(self.baidu_frame, text="百度 App ID:")
        self.baidu_appid_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.baidu_appid_entry = tk.Entry(self.baidu_frame, width=50)
        self.baidu_appid_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

        self.baidu_secret_key_label = tk.Label(self.baidu_frame, text="百度 Secret Key:")
        self.baidu_secret_key_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.baidu_secret_key_entry = tk.Entry(self.baidu_frame, width=50)
        self.baidu_secret_key_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        self.baidu_frame.grid_columnconfigure(1, weight=1)

    def create_bing_tab(self):
        self.bing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bing_frame, text="Bing")

        self.bing_subscription_key_label = tk.Label(self.bing_frame, text="订阅密钥:")
        self.bing_subscription_key_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.bing_subscription_key_entry = tk.Entry(self.bing_frame, width=50)
        self.bing_subscription_key_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

        self.bing_region_label = tk.Label(self.bing_frame, text="区域:")
        self.bing_region_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.bing_region_entry = tk.Entry(self.bing_frame, width=50)
        self.bing_region_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        self.bing_frame.grid_columnconfigure(1, weight=1)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        self.directory_path.set(directory)
    
    def start_translation(self):
        directory_path = self.directory_path.get()
        target_language = self.languages.get(self.selected_language.get())
        proxy = self.proxy_entry.get()

        tab = self.notebook.index(self.notebook.select())
        if tab == 0:  # Google
            api_key = self.google_api_key_entry.get()
            translation_service = "Google"
            extra_params = {}
        elif tab == 1:  # Baidu
            api_key = ""
            translation_service = "Baidu"
            extra_params = {
                'appid': self.baidu_appid_entry.get(),
                'secret_key': self.baidu_secret_key_entry.get()
            }
        elif tab == 2:  # Bing
            api_key = self.bing_subscription_key_entry.get()
            translation_service = "Bing"
            extra_params = {
                'region': self.bing_region_entry.get()
            }

        if directory_path and target_language and ((translation_service == "Google" and api_key) or (translation_service == "Baidu" and extra_params['appid'] and extra_params['secret_key']) or (translation_service == "Bing" and api_key and extra_params['region'])):
            filenames = get_filenames_in_directory(directory_path)
            total_files = len(filenames)
            results = {'success': 0, 'failed': 0, 'failed_files': []}

            start_time = time.time()

            self.progress["value"] = 0
            self.progress["maximum"] = total_files
            self.result_text.delete(1.0, tk.END)
            self.log_text.delete(1.0, tk.END)

            for index, filename in enumerate(filenames):
                translate_and_rename_file(filename, target_language, directory_path, api_key, proxy, results, translation_service, extra_params, self.log_text, index + 1, total_files)
                self.progress["value"] = index + 1
                self.root.update_idletasks()

            if results['failed'] > 0:
                retry_failed_translations(results['failed_files'], target_language, directory_path, api_key, proxy, results, translation_service, extra_params, self.log_text)

            end_time = time.time()
            elapsed_time = end_time - start_time

            # 显示结果
            result_message = f"总文件数: {total_files}\n成功翻译: {results['success']}\n失败翻译: {results['failed']}\n耗时: {elapsed_time:.2f} 秒"
            self.result_text.insert(tk.END, result_message)
        else:
            self.result_text.insert(tk.END, "请填写所有必需的字段\n")

    def open_directory(self):
        directory_path = self.directory_path.get()
        if directory_path:
            subprocess.Popen(["explorer", os.path.realpath(directory_path)])

def resource_path(relative_path):
    """获取资源文件的路径，适配开发和打包环境"""
    if getattr(sys, 'frozen', False):  # 是否是打包环境
        base_path = sys._MEIPASS
    else:  # 开发环境
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 创建主窗口
if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationApp(root)
    icon_path = resource_path("my_icon.ico")
    root.iconbitmap(icon_path)  # 使用动态路径
    root.mainloop()
