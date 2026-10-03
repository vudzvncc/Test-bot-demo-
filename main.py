##############################################################
#                                                                              #
#                    ╔══════════════════════════════════════════════════════╗   #
#                    ║  Made by deleteduserf0bd3b64                        ║   #
#                    ║  Vui lòng ghi công lại tác giả gốc nếu bạn muốn    ║   #
#                    ║  tái tạo lại đoạn mã này.                          ║   #
#                    ║  Link server support: https://discord.gg/eCx2NwAPwA ║   #
#                    ╚══════════════════════════════════════════════════════╝   #
#                                                                              #
##############################################################


# Patch Gateway nhận dạng để hiển thị dưới dạng VR

def patch_gateway_identify():
    async def patched_identify(self):
        version = getattr(self, 'version', 10)
        intents_value = None
        if hasattr(self, '_intents'):
            intents_value = self._intents.value if hasattr(self._intents, 'value') else self._intents
        elif hasattr(self, '_connection') and hasattr(self._connection, 'intents'):
            intents_value = self._connection.intents.value if hasattr(self._connection.intents, 'value') else self._connection.intents
        elif hasattr(self, 'intents'):
            intents_value = self.intents.value if hasattr(self.intents, 'value') else self.intents
        else:
            intents_value = 0

        payload = {
            "op": self.IDENTIFY,
            "d": {
                "token": self.token,
                "capabilities": 16383,
                "properties": {
                    "$os": "android",
                    "$browser": "Discord VR",
                    "$device": "Meta Quest 3",
                },
                "presence": {
                    "status": "online",
                    "activities": [],
                    "afk": False,
                    "since": None,
                },
                "compress": True,
                "large_threshold": 250,
                "v": version,
                "intents": intents_value,
            },
        }
        await self.send(json.dumps(payload))
        self._identify_payload = payload["d"]

    discord.gateway.DiscordWebSocket.identify = patched_identify
    print("[PATCH] Gateway identify patched for VR Device.")

patch_gateway_identify()
import os
import time
import asyncio
import threading
from datetime import datetime, timezone, timedelta

import discord
from discord import app_commands
from flask import Flask
import requests

# ---------- Flask (giữ bot sống trên Render) ----------
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot đang chạy!"


@app.route("/health")
def health():
    return "ok"


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


# ---------- Discord bot ----------
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

VN_TZ = timezone(timedelta(hours=7))  # Giờ Việt Nam (UTC+7)
THU = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]


def do_http_ping():
    """Đo thời gian gọi HTTP tới Discord API (chạy trong thread riêng)."""
    start = time.perf_counter()
    r = requests.get("https://discord.com/api/v10/gateway", timeout=10)
    r.raise_for_status()
    return round((time.perf_counter() - start) * 1000)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Đã đăng nhập: {client.user} (ID: {client.user.id})")


@tree.command(name="ping", description="Xem tốc độ mạng của bot bây giờ")
async def ping(interaction: discord.Interaction):
    await interaction.response.defer()

    ws_ping = round(client.latency * 1000)

    try:
        loop = asyncio.get_running_loop()
        http_ping = await loop.run_in_executor(None, do_http_ping)
        http_text = f"{http_ping} ms"
    except Exception:
        http_text = "Lỗi khi đo"

    embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
    embed.add_field(name="WebSocket", value=f"{ws_ping} ms", inline=True)
    embed.add_field(name="HTTP API", value=http_text, inline=True)
    await interaction.followup.send(embed=embed)


@tree.command(name="dongho", description="Xem thời gian hiện tại")
async def dongho(interaction: discord.Interaction):
    now = datetime.now(VN_TZ)
    embed = discord.Embed(title="🕒 Đồng hồ", color=discord.Color.blue())
    embed.add_field(name="Giờ", value=now.strftime("%H:%M:%S"), inline=True)
    embed.add_field(
        name="Ngày",
        value=f"{THU[now.weekday()]}, {now.strftime('%d/%m/%Y')}",
        inline=True,
    )
    embed.set_footer(text="Múi giờ: Việt Nam (UTC+7)")
    await interaction.response.send_message(embed=embed)


if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit("Thiếu biến môi trường DISCORD_TOKEN")

    threading.Thread(target=run_flask, daemon=True).start()
    client.run(token)
