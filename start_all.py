#!/usr/bin/env python3
"""
Launcher script for Kami Bot with multiple modes:
- Classic Bot: Traditional bot with web interface
- Voice Live: Real-time voice conversation with Azure Voice Live API
"""

import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

class KamiBotLauncher:
    def __init__(self):
        self.bot_process = None
        self.web_process = None
        self.voice_live_process = None
        self.running = True
        self.mode = "classic"  # "classic" or "voice-live"
        
    def start_bot(self):
        """Start the bot server"""
        print("🤖 Starting bot server...")
        try:
            self.bot_process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Bot output monitor
            def monitor_bot():
                for line in iter(self.bot_process.stdout.readline, ''):
                    if line.strip():
                        print(f"🤖 BOT: {line.strip()}")
                    if not self.running:
                        break
            
            # Monitor de erros do bot
            def monitor_bot_errors():
                for line in iter(self.bot_process.stderr.readline, ''):
                    if line.strip():
                        print(f"🚨 BOT ERROR: {line.strip()}")
                    if not self.running:
                        break
            
            threading.Thread(target=monitor_bot, daemon=True).start()
            threading.Thread(target=monitor_bot_errors, daemon=True).start()
            
            return True
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
            return False
    
    def start_web_server(self):
        """Start the web client server"""
        print("🌐 Starting web client server...")
        try:
            self.web_process = subprocess.Popen(
                [sys.executable, "start_web_client.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Web server output monitor
            def monitor_web():
                for line in iter(self.web_process.stdout.readline, ''):
                    if line.strip():
                        print(f"🌐 WEB: {line.strip()}")
                    if not self.running:
                        break
            
            # Monitor de erros do servidor web
            def monitor_web_errors():
                for line in iter(self.web_process.stderr.readline, ''):
                    if line.strip():
                        print(f"🚨 WEB ERROR: {line.strip()}")
                    if not self.running:
                        break
            
            threading.Thread(target=monitor_web, daemon=True).start()
            threading.Thread(target=monitor_web_errors, daemon=True).start()
            
            return True
        except Exception as e:
            print(f"❌ Error starting web server: {e}")
            return False
    
    def start_voice_live(self):
        """Start the Voice Live bot server"""
        print("🎙️ Starting Voice Live bot server...")
        try:
            self.voice_live_process = subprocess.Popen(
                [sys.executable, "voice_live_bot.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Voice Live output monitor
            def monitor_voice_live():
                for line in iter(self.voice_live_process.stdout.readline, ''):
                    if line.strip():
                        print(f"🎙️ VOICE: {line.strip()}")
                    if not self.running:
                        break
            
            # Voice Live error monitor
            def monitor_voice_live_errors():
                for line in iter(self.voice_live_process.stderr.readline, ''):
                    if line.strip():
                        print(f"🚨 VOICE ERROR: {line.strip()}")
                    if not self.running:
                        break
            
            threading.Thread(target=monitor_voice_live, daemon=True).start()
            threading.Thread(target=monitor_voice_live_errors, daemon=True).start()
            
            return True
        except Exception as e:
            print(f"❌ Error starting Voice Live server: {e}")
            return False
    
    def wait_for_services(self):
        """Wait for services to become available"""
        import requests
        
        print("⏳ Waiting for services to become available...")
        
        # Wait for bot
        bot_ready = False
        for i in range(30):  # 30 attempts
            try:
                response = requests.get("http://localhost:3978", timeout=1)
                bot_ready = True
                print("✅ Bot is responding!")
                break
            except:
                time.sleep(1)
                print(f"⏳ Waiting for bot... ({i+1}/30)")
        
        # Wait for web server
        web_ready = False
        for i in range(10):  # 10 attempts
            try:
                response = requests.get("http://localhost:8080", timeout=1)
                web_ready = True
                print("✅ Web server is responding!")
                break
            except:
                time.sleep(1)
                print(f"⏳ Waiting for web server... ({i+1}/10)")
        
        return bot_ready and web_ready
    
    def wait_for_voice_live(self):
        """Wait for Voice Live service to become available"""
        import requests
        
        print("⏳ Waiting for Voice Live service...")
        
        for i in range(15):  # 15 attempts
            try:
                response = requests.get("http://localhost:3978/voice-live", timeout=1)
                print("✅ Voice Live is ready!")
                return True
            except:
                time.sleep(1)
                print(f"⏳ Waiting for Voice Live... ({i+1}/15)")
        
        return False
    
    def show_status(self):
        """Show services status"""
        print("\n" + "="*60)
        print(f"🚀 KAMI BOT - {self.mode.upper()} MODE STATUS")
        print("="*60)
        
        if self.mode == "classic":
            # Bot status
            if self.bot_process and self.bot_process.poll() is None:
                print("🤖 Bot: ✅ RUNNING at http://localhost:3978")
            else:
                print("🤖 Bot: ❌ STOPPED")
            
            # Web server status
            if self.web_process and self.web_process.poll() is None:
                print("🌐 Web: ✅ RUNNING at http://localhost:8080")
            else:
                print("🌐 Web: ❌ STOPPED")
            
            print("\n🔗 ACCESS LINKS:")
            print("• Web Client: http://localhost:8080/voice-client.html")
            print("• Bot API: http://localhost:3978/api/messages")
        
        elif self.mode == "voice-live":
            # Voice Live status
            if self.voice_live_process and self.voice_live_process.poll() is None:
                print("🎙️ Voice Live: ✅ RUNNING at http://localhost:3978")
            else:
                print("🎙️ Voice Live: ❌ STOPPED")
            
            print("\n🔗 ACCESS LINKS:")
            print("• Voice Live Interface: http://localhost:3978/voice-live")
            print("• Main Portal: http://localhost:3978")
        
        print("\n🎯 AVAILABLE FEATURES:")
        if self.mode == "classic":
            print("• 🎤 Voice recognition in English")
            print("• 🔊 Voice synthesis in responses")
            print("• 🧠 Azure GPT-4o AI")
            print("• 💬 Real-time chat")
        else:
            print("• 🎙️ Real-time voice conversation")
            print("• 🧠 Azure AI Foundry integration")
            print("• 🔊 Natural voice synthesis")
            print("• ⚡ Low-latency responses")
        
        print("\n📋 COMMANDS:")
        print("• Ctrl+C: Stop all services")
        print("• Type 'status': Check status")
        print("• Type 'test': Run connectivity test")
        print()
    
    def select_mode(self):
        """Let user select bot mode"""
        print("🤖 KAMI BOT LAUNCHER")
        print("="*50)
        print("Select mode:")
        print("1. 🎮 Classic Bot (Bot Framework + Web Client)")
        print("2. 🎙️ Voice Live (Real-time Voice Conversation)")
        print()
        
        while True:
            try:
                choice = input("Enter your choice (1 or 2): ").strip()
                if choice == "1":
                    self.mode = "classic"
                    print("✅ Classic Bot mode selected")
                    break
                elif choice == "2":
                    self.mode = "voice-live"
                    print("✅ Voice Live mode selected")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1 or 2.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)
    
    def test_connectivity(self):
        """Test services connectivity"""
        import requests
        
        print("🧪 Testing connectivity...")
        
        # Test bot
        try:
            response = requests.get("http://localhost:3978", timeout=5)
            print("✅ Bot: Connectivity OK")
        except Exception as e:
            print(f"❌ Bot: Connectivity error - {e}")
        
        # Test web server
        try:
            response = requests.get("http://localhost:8080", timeout=5)
            print("✅ Web: Connectivity OK")
        except Exception as e:
            print(f"❌ Web: Connectivity error - {e}")
        
        # Test bot API
        try:
            response = requests.options("http://localhost:3978/api/messages", timeout=5)
            print(f"✅ Bot API: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Bot API: Error - {e}")
    
    def stop_services(self):
        """Stop all services"""
        print("\n🛑 Stopping services...")
        self.running = False
        
        if self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=5)
                print("✅ Bot stopped")
            except:
                self.bot_process.kill()
                print("🔥 Bot force stopped")
        
        if self.web_process:
            try:
                self.web_process.terminate()
                self.web_process.wait(timeout=5)
                print("✅ Web server stopped")
            except:
                self.web_process.kill()
                print("🔥 Web server force stopped")
        
        if self.voice_live_process:
            try:
                self.voice_live_process.terminate()
                self.voice_live_process.wait(timeout=5)
                print("✅ Voice Live stopped")
            except:
                self.voice_live_process.kill()
                print("🔥 Voice Live force stopped")
    
    def run(self):
        """Main execution"""
        # Select mode first
        self.select_mode()
        print()
        
        # Check if files exist
        if self.mode == "classic":
            if not Path("app.py").exists():
                print("❌ app.py file not found!")
                return
            
            if not Path("start_web_client.py").exists():
                print("❌ start_web_client.py file not found!")
                return
        
        elif self.mode == "voice-live":
            if not Path("voice_live_bot.py").exists():
                print("❌ voice_live_bot.py file not found!")
                return
        
        # Configure Ctrl+C handler
        def signal_handler(sig, frame):
            print("\n⚠️ Interrupt signal received...")
            self.stop_services()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            if self.mode == "classic":
                # Start classic bot + web client
                bot_started = self.start_bot()
                time.sleep(2)  # Wait a bit between starts
                
                web_started = self.start_web_server()
                
                if not bot_started or not web_started:
                    print("❌ Failed to start some services")
                    self.stop_services()
                    return
                
                # Wait for services to be ready
                services_ready = self.wait_for_services()
                
                if services_ready:
                    self.show_status()
                    
                    # Auto-open browser
                    time.sleep(2)
                    try:
                        import webbrowser
                        webbrowser.open("http://localhost:8080/voice-client.html")
                        print("🌐 Browser opened to web client")
                    except:
                        print("⚠️ Could not auto-open browser")
                else:
                    print("❌ Services did not start properly")
                    self.stop_services()
                    return
            
            elif self.mode == "voice-live":
                # Start Voice Live bot
                voice_live_started = self.start_voice_live()
                
                if not voice_live_started:
                    print("❌ Failed to start Voice Live service")
                    self.stop_services()
                    return
                
                # Wait for Voice Live to be ready
                voice_live_ready = self.wait_for_voice_live()
                
                if voice_live_ready:
                    self.show_status()
                    
                    # Auto-open browser to Voice Live interface
                    time.sleep(2)
                    try:
                        import webbrowser
                        webbrowser.open("http://localhost:3978/voice-live")
                        print("🌐 Browser opened to Voice Live interface")
                    except:
                        print("⚠️ Could not auto-open browser")
                else:
                    print("❌ Voice Live service did not start properly")
                    self.stop_services()
                    return
            
            # Main loop - wait for commands (for both modes)
            print("💡 Type 'help' to see available commands")
            while self.running:
                try:
                    user_input = input("KAMI> ").strip().lower()
                    
                    if user_input == 'status':
                        self.show_status()
                    elif user_input == 'test':
                        if self.mode == "classic":
                            self.test_connectivity()
                        else:
                            print("🧪 Testing Voice Live connectivity...")
                            try:
                                import requests
                                response = requests.get("http://localhost:3978/voice-live", timeout=5)
                                print("✅ Voice Live: Connectivity OK")
                            except Exception as e:
                                print(f"❌ Voice Live: Connectivity error - {e}")
                    elif user_input == 'help':
                        print("📋 Available commands:")
                        print("• status - Show services status")
                        print("• test - Test connectivity")
                        print("• quit/exit - Exit")
                        print("• Ctrl+C - Stop all services")
                    elif user_input in ['quit', 'exit']:
                        break
                    elif user_input:
                        print("❓ Command not recognized. Type 'help' to see commands.")
                
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
        
        except Exception as e:
            print(f"❌ Error during execution: {e}")
        finally:
            self.stop_services()

def main():
    """Main function"""
    launcher = KamiBotLauncher()
    launcher.run()

if __name__ == "__main__":
    main()