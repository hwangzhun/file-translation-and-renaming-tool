import os
import tkinter as tk
from translation_services import translate_text_google, translate_text_baidu, translate_text_bing
import time

def get_filenames_in_directory(directory):
    filenames = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            filenames.append(filename)
    return filenames

def translate_and_rename_file(filename, target_language, directory_path, api_key, proxy, results, translation_service, extra_params, log_text, file_index, total_files):
    try:
        name, extension = os.path.splitext(filename)
        log_text.insert(tk.END, f"翻译中！（{file_index}/{total_files}） {filename}\n", 'black')

        if translation_service == "Google":
            translated_name = translate_text_google(name, target_language, api_key, proxy)
        elif translation_service == "Baidu":
            translated_name = translate_text_baidu(name, target_language, extra_params['appid'], extra_params['secret_key'], proxy)
        elif translation_service == "Bing":
            translated_name = translate_text_bing(name, target_language, api_key, extra_params['region'], proxy)
        
        new_filename = translated_name + extension
        os.rename(os.path.join(directory_path, filename), os.path.join(directory_path, new_filename))
        results['success'] += 1
        log_text.insert(tk.END, f"成功！（{file_index}/{total_files}） {filename} 重命名为 {new_filename}\n", 'green')
    except Exception as e:
        results['failed'] += 1
        results['failed_files'].append(filename)
        log_text.insert(tk.END, f"失败！（{file_index}/{total_files}） {filename}\n", 'red')

def retry_failed_translations(failed_files, target_language, directory_path, api_key, proxy, results, translation_service, extra_params, log_text, max_retries=3):
    log_text.insert(tk.END, "重试翻译失败的文件...\n")
    retries = 0
    while retries < max_retries and failed_files:
        log_text.insert(tk.END, f"重试次数: {retries + 1}\n")
        current_failed_files = failed_files.copy()
        failed_files.clear()
        for index, filename in enumerate(current_failed_files):
            translate_and_rename_file(filename, target_language, directory_path, api_key, proxy, results, translation_service, extra_params, log_text, index + 1, len(current_failed_files))
        retries += 1
        if failed_files:
            log_text.insert(tk.END, f"还有 {len(failed_files)} 个文件重命名失败，将再次重试...\n")
            time.sleep(2)  # 添加延迟，防止快速重试导致问题
    if failed_files:
        log_text.insert(tk.END, f"重试完成后仍有 {len(failed_files)} 个文件重命名失败。\n")
    else:
        log_text.insert(tk.END, "所有文件重试翻译成功。\n")
