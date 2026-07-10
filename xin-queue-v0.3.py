import time
import re
import sys, os
import tkinter as tk
from tkinter import filedialog, messagebox
import win32gui, win32con, win32api

print("xin服队列回答脚本 v0.3 By EJIAOFEN\n")

# ========== 全局变量 ==========
TARGET_HWND = None
cfg_file = 'xin-queue-tool-cfg.txt'

# ========== 创建默认配置 ==========
if not os.path.exists(cfg_file):
    with open(cfg_file, 'w', encoding='utf-8') as f:
        f.write('# 这是xin-queue-tool脚本的配置文件, 你可以在下面更改"="等号后的值以配置脚本\n\n')
        f.write('# Minecraft 日志路径 若带空格请使用英文双引号("")包裹\nlog_path = None\n')
        f.write('# 绑定窗口倒数秒数\ncount_time = 10\n')

# ========== 读取配置 ==========
keys = ['log_path', 'count_time']
keys.sort(key=len, reverse=True)

config = {}
with open(cfg_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if '=' not in line:
            continue
        for key in keys:
            if key in line:   # 备 line.lstrip().startswith(key + '=')
                config[key] = line.split('=', 1)[1].lstrip()
                break

log_path = config.get('log_path')
count_time = config.get('count_time')
try:
    count_time = int(count_time) if count_time is not None else 10
except ValueError:
    count_time = 10

# ========== 选择日志文件函数 ==========
def select_log_file():
    # 如果配置中有有效路径，直接使用
    if log_path and log_path != 'None' and os.path.exists(log_path):
        return log_path
    # 否则弹出选择框
    root = tk.Tk()
    root.withdraw()
    print("选择你的日志文件")
    print("它可能会在以下两个地方:")
    print(".minecraft\\versions\\<版本名称>\\logs\\latest.log")
    print(".minecraft\\logs\\latest.log")
    file_path = filedialog.askopenfilename(
        title="选择 Minecraft 日志文件",
        filetypes=[("日志文件", "latest.log"), ("所有文件", "*.*")]
    )
    print(f"\n你可以检查脚本同文件夹下的 {cfg_file} 以预设置日志路径")
    root.destroy()
    return file_path

# ========== 预设键值映射 ==========
KEYWORD_MAP = {
    "南瓜": "不需要",
    "最快": "金",
    "火把": "15",
    "无限": "3",
    "定位": "0",
    "凋灵": "下界之星",
    "大箱子": "54",
    "小箱子": "27",
    "羊驼": "不会",
    "年份": "2020"
}

# ========== 绑定窗口 ==========
def bind_window():
    global TARGET_HWND
    print("\n=== 绑定 Minecraft 窗口 ===")
    print(f"请在接下来的 {count_time} 秒内将 Minecraft 游戏窗口激活(点击窗口使其处于最前方). ")
    for i in range(count_time, 0, -1):
        print(f"倒计时 {i} 秒...")
        time.sleep(1)
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        print("错误：无法获取前台窗口句柄.")
        return False
    title = win32gui.GetWindowText(hwnd)
    print(f"捕获到前台窗口：标题 = '{title}', 句柄 = {hwnd}")
    TARGET_HWND = hwnd
    print(f"成功绑定窗口：{title}\n")
    return True

# ========== 工具函数 ==========
def follow_log(file_path):
    with open(file_path, 'r', encoding='gb18030', errors='ignore') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                time.sleep(0.1)

def find_option_char(line, keyword_value):
    index = line.rfind(keyword_value)
    if index == -1:
        return None
    if index >= 2:
        return line[index - 2]
    else:
        return None

def send_answer(option_char):
    global TARGET_HWND
    if TARGET_HWND is None:
        print("错误：未绑定窗口")
        return
    if not win32gui.IsWindow(TARGET_HWND):
        print("错误：绑定的窗口已关闭")
        return

    win32api.PostMessage(TARGET_HWND, win32con.WM_CHAR, ord(option_char), 0)
    time.sleep(0.05)
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    time.sleep(0.05)
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYDOWN, ord('T'), 0)
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYUP, ord('T'), 0)
    print(f"已发送答案: {option_char}\n")

# ========== 主程序 ==========
def main():
    global TARGET_HWND

    LOG_PATH = select_log_file()
    if not LOG_PATH:
        print("未选择日志文件, 程序退出.")
        return

    if not bind_window():
        return

    print("正在初始化聊天框状态...")
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)
    time.sleep(0.1)
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYDOWN, ord('T'), 0)
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYUP, ord('T'), 0)
    time.sleep(0.2)
    print("聊天框已打开, 开始监控日志...\n")
    print("注意：请确保游戏内未打开其他界面(如物品栏), 输入法为英文. \n")
    

    for line in follow_log(LOG_PATH):
        if "[CHAT]" not in line:
            continue

        # 检测玩家发言，退出
        if re.search(r'<', line):
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("xin-queue-tool", "排队完成! 脚本已关闭.")
            root.destroy()
            sys.exit(0)

        matched_key = None
        matched_value = None
        for key, value in KEYWORD_MAP.items():
            if key in line:
                matched_key = key
                matched_value = value
                break

        if matched_key is None:
            continue

        print(f"找到关键词 '{matched_key}': {line.strip()}")
        option_char = find_option_char(line, matched_value)
        if option_char is None:
            print(f"未找到 '{matched_value}', 或位置过于靠前.")
            continue

        print(f"提取答案: {option_char}")
        send_answer(option_char)

if __name__ == "__main__":
    main()