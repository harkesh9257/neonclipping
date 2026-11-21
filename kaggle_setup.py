"""
1-Click Kaggle Runner for NeonClipping on 2x T4 GPUs with Cloudflare Tunnel.
Run this directly in Kaggle Notebook:
    !python kaggle_setup.py
"""
import os, subprocess, time, re, sys

print("🚀 Setting up NeonClipping on Kaggle T4 GPUs (32GB VRAM)...")

# 1. Install dependencies
subprocess.run(["pip", "install", "-q", "-r", "requirements.txt"], check=False)

# 2. Setup Ollama
print("📦 Setting up Ollama with GPU acceleration...")
subprocess.run(["apt-get", "update", "-y"], check=False)
subprocess.run(["apt-get", "install", "-y", "zstd"], check=False)
subprocess.run(["sh", "-c", "curl -fsSL https://ollama.com/install.sh | sh"], check=True)
subprocess.Popen(["ollama", "serve"])
time.sleep(5)

# 3. Pull AI models suited for 16GB+ VRAM
print("🤖 Pulling Llama 3.2 3B & Vision Models...")
subprocess.run(["ollama", "pull", "llama3.2:3b"])
# Optional high-quality vision model:
subprocess.run(["ollama", "pull", "llama3.2-vision:11b"])

# 4. Download Cloudflare tunnel
print("🌐 Setting up Cloudflare tunnel...")
subprocess.run(["wget", "-q", "-nc", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"])
subprocess.run(["chmod", "+x", "cloudflared-linux-amd64"])

# 5. Launch NeonClipping
print("⚡ Starting NeonClipping Server...")
env = os.environ.copy()
env["NEONCLIPPING_LAN"] = "1"
subprocess.Popen(["python3", "app.py"], env=env)
time.sleep(4)

# 6. Start tunnel and expose public URL
tunnel = subprocess.Popen(
    ["./cloudflared-linux-amd64", "tunnel", "--url", "http://127.0.0.1:8770"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

print("\n" + "=" * 60)
print("Connecting tunnel... Aapka link generate ho raha hai:")
for line in tunnel.stdout:
    match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
    if match:
        url = match.group(0)
        print("\n" + "=" * 60)
        print("🎉 AAPKA NEONCLIPPING LINK LIVE HAI:")
        print(f"👉 Web App:       {url}")
        print(f"👉 Mobile Remote: {url}/m")
        print("=" * 60 + "\n")
        break

try:
    tunnel.wait()
except KeyboardInterrupt:
    pass
