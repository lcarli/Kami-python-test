#!/usr/bin/env python3
"""
Script para iniciar o Kami Bot e o servidor web do cliente simultaneamente
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
        self.running = True
        
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
    
    def show_status(self):
        """Show services status"""
        print("\n" + "="*60)
        print("🚀 KAMI BOT - SERVICES STATUS")
        print("="*60)
        
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
        
        print("\n🎯 AVAILABLE FEATURES:")
        print("• 🎤 Voice recognition in English")
        print("• 🔊 Voice synthesis in responses")
        print("• 🧠 Azure GPT-4o AI")
        print("• 💬 Real-time chat")
        
        print("\n📋 COMMANDS:")
        print("• Ctrl+C: Stop all services")
        print("• Type 'status': Check status")
        print("• Type 'test': Run connectivity test")
        print()
    
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
    
    def run(self):
        """Main execution"""
        print("🚀 KAMI BOT LAUNCHER")
        print("="*40)
        
        # Check if files exist
        if not Path("app.py").exists():
            print("❌ app.py file not found!")
            return
        
        if not Path("start_web_client.py").exists():
            print("❌ start_web_client.py file not found!")
            return
        
        # Configure Ctrl+C handler
        def signal_handler(sig, frame):
            print("\n⚠️ Interrupt signal received...")
            self.stop_services()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            # Start services
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
                
                # Main loop - wait for commands
                print("💡 Type 'help' to see available commands")
                while self.running:
                    try:
                        user_input = input("KAMI> ").strip().lower()
                        
                        if user_input == 'status':
                            self.show_status()
                        elif user_input == 'test':
                            self.test_connectivity()
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
            else:
                print("❌ Services did not become ready in time")
            
        finally:
            self.stop_services()

def main():
    """Main function"""
    launcher = KamiBotLauncher()
    launcher.run()

if __name__ == "__main__":
    main()