import http.server
import socketserver
import socket
import os
import json
import urllib.parse

# === 配置 ===
from config import (
    CONFIG_FILE, DEFAULT_PROMPT_FILE, SAVES_DIR, PRESETS_DIR, LOGS_DIR, HTML_FILE,
    load_config, save_config
)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # API: 获取配置
        if path == '/api/config':
            self.send_json(load_config())
            return

        # API: 获取默认 Prompt
        if path == '/api/default_prompt':
            if os.path.exists(DEFAULT_PROMPT_FILE):
                with open(DEFAULT_PROMPT_FILE, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                self.send_error(404, "Default prompt file not found")
            return

        # API: 列出存档
        if path == '/api/saves':
            files = [f for f in os.listdir(SAVES_DIR) if f.endswith('.json')]
            self.send_json(files)
            return

        # API: 获取存档内容
        if path.startswith('/api/saves/'):
            filename = path.split('/')[-1]
            filepath = os.path.join(SAVES_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                self.send_error(404, "Save file not found")
            return

        # API: 列出预设
        if path == '/api/presets':
            files = [f for f in os.listdir(PRESETS_DIR) if f.endswith('.json')]
            self.send_json(files)
            return

        # API: 获取预设内容
        if path.startswith('/api/presets/'):
            filename = path.split('/')[-1]
            filepath = os.path.join(PRESETS_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.send_json(json.load(f))
            else:
                self.send_error(404, "Preset file not found")
            return

        # 默认行为：访问根目录指向 wolf.html
        if path == '/':
            self.path = '/' + HTML_FILE
        
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        length = int(self.headers.get('content-length', 0))
        data = self.rfile.read(length)
        try:
            json_data = json.loads(data)
        except:
            json_data = {}

        # API: 保存配置
        if path == '/api/config':
            current_config = load_config()
            # 只更新允许的字段
            if 'apiBase' in json_data: current_config['apiBase'] = json_data['apiBase']
            if 'apiKey' in json_data: current_config['apiKey'] = json_data['apiKey']
            if 'rolesSetup' in json_data: current_config['rolesSetup'] = json_data['rolesSetup']
            if 'modelsSetup' in json_data: current_config['modelsSetup'] = json_data['modelsSetup']
            # port 不允许通过 API 修改，因为需要重启服务器
            save_config(current_config)
            self.send_json({"status": "ok"})
            return

        # API: 保存存档
        if path.startswith('/api/saves/'):
            filename = path.split('/')[-1]
            if not filename.endswith('.json'): filename += '.json'
            filepath = os.path.join(SAVES_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
            self.send_json({"status": "ok"})
            return

        # API: 保存预设
        if path.startswith('/api/presets/'):
            filename = path.split('/')[-1]
            if not filename.endswith('.json'): filename += '.json'
            filepath = os.path.join(PRESETS_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
            self.send_json({"status": "ok"})
            return

        # API: 记录调试日志
        if path == '/api/debug_log':
            filepath = os.path.join(LOGS_DIR, 'latest.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
            self.send_json({"status": "ok"})
            return

        self.send_error(404, "API endpoint not found")

    def do_DELETE(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # API: 删除存档
        if path.startswith('/api/saves/'):
            filename = path.split('/')[-1]
            filepath = os.path.join(SAVES_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                self.send_json({"status": "ok"})
            else:
                self.send_error(404, "File not found")
            return

        # API: 删除预设
        if path.startswith('/api/presets/'):
            filename = path.split('/')[-1]
            filepath = os.path.join(PRESETS_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                self.send_json({"status": "ok"})
            else:
                self.send_error(404, "File not found")
            return
            
        self.send_error(404, "API endpoint not found")

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def start_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 确保目录存在
    if not os.path.exists(SAVES_DIR): os.makedirs(SAVES_DIR)
    if not os.path.exists(PRESETS_DIR): os.makedirs(PRESETS_DIR)
    if not os.path.exists(LOGS_DIR): os.makedirs(LOGS_DIR)

    config = load_config()
    port = config.get('port', 169)
    
    handler = MyHandler
    
    try:
        httpd = socketserver.TCPServer(("", port), handler)
    except OSError as e:
        print(f"[错误] 无法启动端口 {port}: {e}")
        return

    ip = get_ip_address()
    
    print("="*40)
    print(f"  🐺 AI 狼人杀服务器已启动!")
    print("="*40)
    print(f"\n📂 文件路径: {os.getcwd()}/{HTML_FILE}")
    print(f"\n👉 本机访问请点击: http://localhost:{port}")
    print(f"👉 局域网(其他手机)访问: http://{ip}:{port}")
    print("\n按 Ctrl+C 停止服务器")
    print("="*40)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已关闭。")
        httpd.shutdown()

if __name__ == "__main__":
    start_server()