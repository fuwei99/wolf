import os
import json

# === 常量定义 ===
CONFIG_FILE = "config.json"
DEFAULT_PROMPT_FILE = "default_prompt.json"
SAVES_DIR = "saves"
PRESETS_DIR = "presets"
LOGS_DIR = "logs"
HTML_FILE = "wolf.html"

# 默认配置，如果 config.json 不存在或读取失败时使用
DEFAULT_CONFIG = {
    "apiBase": "https://newapi.maltobitoo.xyz/v1",
    "apiKey": "",
    "port": 169
}

def load_config():
    """
    加载配置。优先级：
    1. 环境变量 CONFIG (JSON 字符串)
    2. 本地文件 config.json
    3. 默认配置
    """
    # 1. 尝试从环境变量读取
    config_env = os.environ.get('CONFIG')
    if config_env:
        try:
            config = json.loads(config_env)
            # 如果是在 Hugging Face 或类似环境运行，强制端口为 7860 或环境变量指定的 PORT
            # 这里的逻辑参考原本 Dockerfile 中的设定
            config['port'] = int(os.environ.get('PORT', 7860))
            
            # 将从环境变量加载的配置保存到本地文件，以便 server.py 正常运行
            save_config(config)
            print("Config initialized from ENV 'CONFIG'")
            return config
        except Exception as e:
            print(f"[错误] 解析环境变量 CONFIG 失败: {e}")

    # 2. 尝试从本地文件读取
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[错误] 读取 {CONFIG_FILE} 失败: {e}")

    # 3. 返回默认配置
    return DEFAULT_CONFIG

def save_config(config):
    """保存配置到本地文件。"""
    try:
        # 确保目录存在（虽然一般在当前目录）
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[错误] 保存配置失败: {e}")
