import time
import psutil
import requests
import pyttsx3
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

def speak_text(text):
    """Re-initializes and speaks text using pyttsx3 to prevent queue freezing."""
    try:
        clean_text = text.replace('AI:', '').replace('Bot:', '').strip()
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        engine.say(clean_text)
        engine.runAndWait()
        engine.stop()
    except Exception:
        pass

class AnomalyEngine:
    def __init__(self, window_size=20, threshold=2.0):
        self.history = []
        self.history_size = window_size  
        self.threshold = threshold

    def check(self, value):
        self.history.append(value)
        if len(self.history) > self.history_size:
            self.history.pop(0)

        if len(self.history) < 5:
            return False, 0.0  # Need a bit of history first

        mean = sum(self.history) / len(self.history)
        variance = sum((x - mean) ** 2 for x in self.history) / len(self.history)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return False, 0.0

        z_score = (value - mean) / std_dev
        is_anomaly = abs(z_score) > self.threshold
        return is_anomaly, z_score

# OLLAMA WITTY AI COMPANION
def get_ollama_commentary(cpu_pct, mem_pct, is_anomaly):
    prompt = (
        f"You are a witty, sarcastic AI living inside a computer's terminal dashboard. "
        f"Current system stats -> CPU: {cpu_pct}%, RAM: {mem_pct}%, Anomaly Alert: {is_anomaly}. "
        f"Give a single, short, witty, and humorous one-liner reacting to this. "
        f"Keep it under 15 words. Do not use quotes."
    )
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "tinyllama",  # Change this if you use a different model like 'mistral' or 'phi3'
                "prompt": prompt,
                "stream": False
            },
            timeout=20.0
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception:
        pass

    return "Hold on..."

# Main dashboard loop
if __name__ == "__main__":
    engine = AnomalyEngine()
    print("Initializing Telemetry Engine & AI Companion... Press Ctrl+C to exit")

    # Prime psutil for accurate initial readings
    psutil.cpu_percent(interval=None)

    # We cache the AI commentary so we don't spam Ollama every half-second
    last_ai_update = 0
    cached_commentary = "Booting up companion core..."

    try:
        with Live(refresh_per_second=2) as live:
            while True:
                # Gather real system metrics
                cpu = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory().percent

                # Check for anomalies
                is_anomaly, z_score = engine.check(cpu)
                
                # Query ollama every 10 seconds to keep commentary fresh without lagging
                current_time = time.time()
                if current_time - last_ai_update > 10:
                    cached_commentary = get_ollama_commentary(cpu, memory, is_anomaly)
                    # Speak the new witty commentary out loud!
                    speak_text(cached_commentary)
                    last_ai_update = current_time

                # Build the Rich Table Layout
                table = Table(title="Live System Telemetry & AI Companion", expand=True)
                table.add_column("Metric", style="cyan", no_wrap=True)
                table.add_column("Value", style="magenta")
                table.add_column("Status / Z-Score", style="green")

                status_str = f"[red]ANOMALY (Z: {z_score:.2f})[/red]" if is_anomaly else "[green]NORMAL[/green]"
                table.add_row("CPU Usage", f"{cpu}%", status_str)
                table.add_row("Memory Usage", f"{memory}%", "Monitoring...")

                # Wrap everything in a nice panel including our AI companion's voice
                panel_content = Panel(
                    table,
                    subtitle=f"[yellow]AI Companion:[/yellow] {cached_commentary}",
                    border_style="blue"
                )

                live.update(panel_content)
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        print("\nTelemetry Engine shut down safely.")