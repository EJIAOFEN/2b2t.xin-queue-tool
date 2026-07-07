import time
import re
import tkinter as tk
from tkinter import filedialog
import win32gui
import win32con
import win32api

# By EJIAOFEN
# 完全就是 Deepseek 写的哈哈哈

print("xin服队列回答脚本 v0.2 By EJIAOFEN\n")

# ========== 全局变量 ==========
TARGET_HWND = None          # 绑定的窗口句柄

# ========== 配置区 ==========
def select_log_file():
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
    root.destroy()
    return file_path if file_path else None

# 预设键值映射
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

# ========== 绑定窗口（自动延时捕获） ==========
def bind_window():
    """提示用户将 Minecraft 窗口置于前台，等待 10 秒后自动捕获"""
    global TARGET_HWND
    print("\n=== 绑定 Minecraft 窗口 ===")
    print("请在接下来的 10 秒内将 Minecraft 游戏窗口激活（点击窗口使其处于最前方）。")
    for i in range(10, 0, -1):
        print(f"倒计时 {i} 秒...")
        time.sleep(1)
    
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        print("错误：无法获取前台窗口句柄。")
        return False
    
    title = win32gui.GetWindowText(hwnd)
    print(f"捕获到前台窗口：标题 = '{title}'，句柄 = {hwnd}")
    
    '''
    # 检查窗口标题是否包含 Minecraft，防止误绑
    if "Minecraft" not in title:
        print("警告：当前前台窗口标题不包含 'Minecraft'，可能不是游戏窗口。")
        print("绑定失败，请确保 Minecraft 窗口在前台，然后重新运行脚本。")
        return False
    '''
    
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
    """向绑定的窗口发送答案（假设聊天框已打开）"""
    global TARGET_HWND
    if TARGET_HWND is None:
        print("错误：未绑定窗口")
        return
    if not win32gui.IsWindow(TARGET_HWND):
        print("错误：绑定的窗口已关闭")
        return

    # 1. 输入选项字母（聊天框已打开）
    win32api.PostMessage(TARGET_HWND, win32con.WM_CHAR, ord(option_char), 0)
    time.sleep(0.05)

    # 2. 按回车发送
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    time.sleep(0.05)

    # 3. 按 t 重新打开聊天框（为下一次准备）
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYDOWN, ord('T'), 0)
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYUP, ord('T'), 0)

    print(f"已发送答案: {option_char}\n")

# ========== 主程序 ==========
def main():
    global TARGET_HWND

    # 1. 选择日志文件
    LOG_PATH = select_log_file()
    if not LOG_PATH:
        print("未选择日志文件，程序退出。")
        return

    # 2. 绑定 Minecraft 窗口
    if not bind_window():
        return

    # 3. 初始化：强制进入聊天框状态（先 ESC 关闭所有界面，再按 t 打开聊天框）
    print("正在初始化聊天框状态...")
    # 先发送 ESC，关闭可能存在的菜单/聊天框
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)
    time.sleep(0.1)
    # 再按 t 打开聊天框
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYDOWN, ord('T'), 0)
    win32api.PostMessage(TARGET_HWND, win32con.WM_KEYUP, ord('T'), 0)
    time.sleep(0.2)
    print("聊天框已打开，开始监控日志...\n")

    print(f"关键词字典: {KEYWORD_MAP}\n")
    print("注意：请确保游戏内未打开其他界面（如物品栏），输入法为英文。\n")

    # 4. 监控日志并自动回答
    for line in follow_log(LOG_PATH):
        if "[CHAT]" not in line:
            continue

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
            print(f"未找到 '{matched_value}', 或位置过于靠前。")
            continue

        print(f"提取答案: {option_char}")
        send_answer(option_char)

if __name__ == "__main__":
    main()