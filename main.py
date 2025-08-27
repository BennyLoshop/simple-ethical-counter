import flet as ft
import threading
import requests
from flask import Flask, request, Response, jsonify

# ---------------- Flask server ----------------
flask_app = Flask(__name__)

@flask_app.route('/proxy/ping')
def ping():
    resp = Response("pong")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@flask_app.route('/proxy/<path:url>', methods=['GET', 'OPTIONS'])
def pic_agent(url):
    if request.method == 'OPTIONS':
        resp = Response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        return resp

    try:
        target_url = url if url.startswith(("http://", "https://")) else f"http://{url}"
        resp = requests.get(target_url, stream=True, timeout=10)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "application/octet-stream")
        response = Response(resp.content, mimetype=content_type)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        return response
    except requests.exceptions.RequestException as e:
        response = jsonify({"success": False, "error": f"获取失败: {str(e)}"})
        response.status_code = 502
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        return response


def run_flask_server():
    # host="0.0.0.0" 表示局域网可访问
    flask_app.run(port=5005)


# ---------------- Flet UI ----------------
def main(page: ft.Page):
    page.title = "助手服务"
    page.window_width = 400
    page.window_height = 200

    status = ft.Text("正在启动服务器...", size=18)
    page.add(status)

    async def start_server():
        threading.Thread(target=run_flask_server, daemon=True).start()
        status.value = "服务器已启动 (端口 5005)"
        page.update()

    page.run_task(start_server)


if __name__ == "__main__":
    ft.app(target=main)
