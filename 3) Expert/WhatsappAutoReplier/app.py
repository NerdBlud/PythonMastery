import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pywhatkit as pwk
from typing import Optional, Dict, List

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class WhatsAppAutomation:
    def __init__(self):
        self.config_dir = Path.home() / '.whatsapp_automation'
        self.config_file = self.config_dir / 'config.json'
        self.contacts_file = self.config_dir / 'contacts.json'
        self.history_file = self.config_dir / 'history.json'
        self.preferences = self.load_preferences()
        self.contacts = self.load_contacts()
        self.ensure_config_directory()
    
    def ensure_config_directory(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
            print(f"{Colors.GREEN}✓ Configuration directory created{Colors.END}")
    
    def load_preferences(self) -> Dict:
        default_prefs = {
            'default_wait_time': 15,
            'close_tab_after_send': True,
            'close_tab_wait_time': 2,
            'chrome_driver_path': None,
            'country_code': '+1',
            'message_history_limit': 50,
            'default_send_now': False
        }
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_prefs = json.load(f)
                    default_prefs.update(loaded_prefs)
            except Exception as e:
                print(f"{Colors.YELLOW}⚠ Error loading preferences: {e}{Colors.END}")
        return default_prefs
    
    def save_preferences(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.preferences, f, indent=4)
            print(f"{Colors.GREEN}✓ Preferences saved successfully{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error saving preferences: {e}{Colors.END}")
    
    def load_contacts(self) -> Dict:
        if self.contacts_file.exists():
            try:
                with open(self.contacts_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"{Colors.YELLOW}⚠ Error loading contacts: {e}{Colors.END}")
        return {}
    
    def save_contacts(self):
        try:
            with open(self.contacts_file, 'w') as f:
                json.dump(self.contacts, f, indent=4)
            print(f"{Colors.GREEN}✓ Contacts saved successfully{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error saving contacts: {e}{Colors.END}")
    
    def add_to_history(self, phone: str, message: str, scheduled_time: str):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            except:
                pass
        history.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'phone': phone,
            'message': message[:50] + '...' if len(message) > 50 else message,
            'scheduled_time': scheduled_time
        })
        history = history[-self.preferences['message_history_limit']:]
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=4)
    
    def print_header(self):
        print(f"\n{Colors.CYAN}{Colors.BOLD}")
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║          WhatsApp Automation CLI Tool v2.0               ║")
        print("║           Professional Message Scheduler                 ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}\n")
    
    def print_menu(self):
        print(f"{Colors.BOLD}Main Menu:{Colors.END}")
        print(f"{Colors.BLUE}1.{Colors.END} Send WhatsApp Message")
        print(f"{Colors.BLUE}2.{Colors.END} Send Instant Message (Now)")
        print(f"{Colors.BLUE}3.{Colors.END} Send Message to Group")
        print(f"{Colors.BLUE}4.{Colors.END} Manage Contacts")
        print(f"{Colors.BLUE}5.{Colors.END} View Message History")
        print(f"{Colors.BLUE}6.{Colors.END} Configure Preferences")
        print(f"{Colors.BLUE}7.{Colors.END} Setup Chrome Driver")
        print(f"{Colors.BLUE}8.{Colors.END} Test Connection (Load QR Code)")
        print(f"{Colors.BLUE}9.{Colors.END} Help & Documentation")
        print(f"{Colors.BLUE}0.{Colors.END} Exit")
        print()
    
    def send_message(self, phone: str, message: str, hour: int, minute: int):
        try:
            print(f"\n{Colors.YELLOW}⏳ Preparing to send message...{Colors.END}")
            print(f"📱 To: {phone}")
            print(f"📝 Message: {message[:50]}...")
            print(f"⏰ Scheduled: {hour:02d}:{minute:02d}")
            pwk.sendwhatmsg(
                phone_no=phone,
                message=message,
                time_hour=hour,
                time_min=minute,
                wait_time=self.preferences['default_wait_time'],
                tab_close=self.preferences['close_tab_after_send'],
                close_time=self.preferences['close_tab_wait_time']
            )
            scheduled_time = f"{hour:02d}:{minute:02d}"
            self.add_to_history(phone, message, scheduled_time)
            print(f"{Colors.GREEN}✓ Message sent successfully!{Colors.END}\n")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Error sending message: {e}{Colors.END}\n")
            return False
    
    def send_instant_message(self, phone: str, message: str):
        try:
            print(f"\n{Colors.YELLOW}⏳ Sending instant message...{Colors.END}")
            print(f"📱 To: {phone}")
            print(f"📝 Message: {message[:50]}...")
            pwk.sendwhatmsg_instantly(
                phone_no=phone,
                message=message,
                wait_time=self.preferences['default_wait_time'],
                tab_close=self.preferences['close_tab_after_send'],
                close_time=self.preferences['close_tab_wait_time']
            )
            self.add_to_history(phone, message, "Instant")
            print(f"{Colors.GREEN}✓ Message sent successfully!{Colors.END}\n")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Error sending message: {e}{Colors.END}\n")
            return False
    
    def send_group_message(self, group_id: str, message: str, hour: int, minute: int):
        try:
            print(f"\n{Colors.YELLOW}⏳ Preparing to send group message...{Colors.END}")
            print(f"👥 Group: {group_id}")
            print(f"📝 Message: {message[:50]}...")
            print(f"⏰ Scheduled: {hour:02d}:{minute:02d}")
            pwk.sendwhatmsg_to_group(
                group_id=group_id,
                message=message,
                time_hour=hour,
                time_min=minute,
                wait_time=self.preferences['default_wait_time'],
                tab_close=self.preferences['close_tab_after_send'],
                close_time=self.preferences['close_tab_wait_time']
            )
            scheduled_time = f"{hour:02d}:{minute:02d}"
            self.add_to_history(f"Group: {group_id}", message, scheduled_time)
            print(f"{Colors.GREEN}✓ Group message sent successfully!{Colors.END}\n")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Error sending group message: {e}{Colors.END}\n")
            return False
    
    def manage_contacts_menu(self):
        while True:
            print(f"\n{Colors.BOLD}Contact Management:{Colors.END}")
            print(f"{Colors.BLUE}1.{Colors.END} Add Contact")
            print(f"{Colors.BLUE}2.{Colors.END} View Contacts")
            print(f"{Colors.BLUE}3.{Colors.END} Delete Contact")
            print(f"{Colors.BLUE}4.{Colors.END} Back to Main Menu")
            choice = input(f"\n{Colors.CYAN}Enter choice: {Colors.END}").strip()
            if choice == '1':
                self.add_contact()
            elif choice == '2':
                self.view_contacts()
            elif choice == '3':
                self.delete_contact()
            elif choice == '4':
                break
    
    def add_contact(self):
        print(f"\n{Colors.BOLD}Add New Contact{Colors.END}")
        name = input("Contact Name: ").strip()
        if not name:
            print(f"{Colors.RED}✗ Name cannot be empty{Colors.END}")
            return
        phone = input(f"Phone Number (with country code, e.g., {self.preferences['country_code']}1234567890): ").strip()
        if not phone.startswith('+'):
            phone = self.preferences['country_code'] + phone
        self.contacts[name] = phone
        self.save_contacts()
        print(f"{Colors.GREEN}✓ Contact '{name}' added successfully{Colors.END}")
    
    def view_contacts(self):
        if not self.contacts:
            print(f"\n{Colors.YELLOW}No contacts saved{Colors.END}")
            return
        print(f"\n{Colors.BOLD}Saved Contacts:{Colors.END}")
        print(f"{Colors.CYAN}{'Name':<20} {'Phone Number':<20}{Colors.END}")
        print("─" * 40)
        for name, phone in self.contacts.items():
            print(f"{name:<20} {phone:<20}")
        print()
    
    def delete_contact(self):
        self.view_contacts()
        if not self.contacts:
            return
        name = input(f"\n{Colors.CYAN}Enter contact name to delete: {Colors.END}").strip()
        if name in self.contacts:
            del self.contacts[name]
            self.save_contacts()
            print(f"{Colors.GREEN}✓ Contact '{name}' deleted{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Contact not found{Colors.END}")
    
    def view_history(self):
        if not self.history_file.exists():
            print(f"\n{Colors.YELLOW}No message history available{Colors.END}")
            return
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            if not history:
                print(f"\n{Colors.YELLOW}No message history available{Colors.END}")
                return
            print(f"\n{Colors.BOLD}Message History:{Colors.END}")
            print(f"{Colors.CYAN}{'Timestamp':<20} {'To':<25} {'Scheduled':<12} {'Message':<30}{Colors.END}")
            print("─" * 90)
            for entry in reversed(history[-20:]):
                print(f"{entry['timestamp']:<20} {entry['phone']:<25} {entry['scheduled_time']:<12} {entry['message']:<30}")
            print()
        except Exception as e:
            print(f"{Colors.RED}✗ Error loading history: {e}{Colors.END}")
    
    def configure_preferences(self):
        while True:
            print(f"\n{Colors.BOLD}Current Preferences:{Colors.END}")
            print(f"1. Default Wait Time: {Colors.GREEN}{self.preferences['default_wait_time']}s{Colors.END}")
            print(f"2. Close Tab After Send: {Colors.GREEN}{self.preferences['close_tab_after_send']}{Colors.END}")
            print(f"3. Tab Close Wait Time: {Colors.GREEN}{self.preferences['close_tab_wait_time']}s{Colors.END}")
            print(f"4. Country Code: {Colors.GREEN}{self.preferences['country_code']}{Colors.END}")
            print(f"5. Message History Limit: {Colors.GREEN}{self.preferences['message_history_limit']}{Colors.END}")
            print(f"6. Chrome Driver Path: {Colors.GREEN}{self.preferences['chrome_driver_path'] or 'Not set'}{Colors.END}")
            print(f"{Colors.BLUE}7.{Colors.END} Back to Main Menu")
            choice = input(f"\n{Colors.CYAN}Select preference to change: {Colors.END}").strip()
            if choice == '1':
                val = input("Enter wait time (seconds, 10-30 recommended): ").strip()
                if val.isdigit():
                    self.preferences['default_wait_time'] = int(val)
                    self.save_preferences()
            elif choice == '2':
                val = input("Close tab after send? (yes/no): ").strip().lower()
                self.preferences['close_tab_after_send'] = val in ['yes', 'y', 'true', '1']
                self.save_preferences()
            elif choice == '3':
                val = input("Enter tab close wait time (seconds): ").strip()
                if val.isdigit():
                    self.preferences['close_tab_wait_time'] = int(val)
                    self.save_preferences()
            elif choice == '4':
                val = input("Enter country code (e.g., +1, +91, +44): ").strip()
                if val.startswith('+'):
                    self.preferences['country_code'] = val
                    self.save_preferences()
            elif choice == '5':
                val = input("Enter history limit (1-1000): ").strip()
                if val.isdigit() and 1 <= int(val) <= 1000:
                    self.preferences['message_history_limit'] = int(val)
                    self.save_preferences()
            elif choice == '6':
                val = input("Enter Chrome driver path (or 'clear' to remove): ").strip()
                if val.lower() == 'clear':
                    self.preferences['chrome_driver_path'] = None
                else:
                    self.preferences['chrome_driver_path'] = val
                self.save_preferences()
            elif choice == '7':
                break
    
    def setup_chrome_driver(self):
        print(f"\n{Colors.BOLD}Chrome Driver Setup{Colors.END}")
        print("If Chrome is not installed, you need to configure the ChromeDriver.")
        print("\nSteps:")
        print("1. Download ChromeDriver from: https://developer.chrome.com/docs/chromedriver/")
        print("2. Extract and note the path to chromedriver.exe")
        print("3. Enter the path below")
        path = input(f"\n{Colors.CYAN}Enter ChromeDriver path (or 'skip' to cancel): {Colors.END}").strip()
        if path.lower() != 'skip':
            try:
                pwk.add_driver_path(path)
                self.preferences['chrome_driver_path'] = path
                self.save_preferences()
                print(f"{Colors.GREEN}✓ Chrome driver configured successfully{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}✗ Error setting driver path: {e}{Colors.END}")
    
    def test_connection(self):
        print(f"\n{Colors.YELLOW}⏳ Loading WhatsApp Web QR Code...{Colors.END}")
        print("Scan the QR code with your phone if not already logged in.")
        try:
            pwk.load_QRcode()
            print(f"{Colors.GREEN}✓ Connection test completed{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error loading QR code: {e}{Colors.END}")
    
    def show_help(self):
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== WhatsApp Automation Help ==={Colors.END}\n")
        print(f"{Colors.BOLD}Features:{Colors.END}")
        print("• Schedule messages to be sent at specific times")
        print("• Send instant messages")
        print("• Send messages to groups")
        print("• Save frequently used contacts")
        print("• View message history")
        print("• Customize preferences\n")
        print(f"{Colors.BOLD}Phone Number Format:{Colors.END}")
        print("• Must include country code (e.g., +11234567890)")
        print("• No spaces or special characters")
        print(f"• Default country code: {self.preferences['country_code']}\n")
        print(f"{Colors.BOLD}Group ID Format:{Colors.END}")
        print("• Open WhatsApp Web")
        print("• Click on the group")
        print("• Check URL: https://web.whatsapp.com/...../GROUPID")
        print("• Use the GROUPID from URL\n")
        print(f"{Colors.BOLD}Requirements:{Colors.END}")
        print("• Chrome browser or ChromeDriver")
        print("• WhatsApp Web must be logged in")
        print("• Internet connection\n")
        print(f"{Colors.BOLD}Tips:{Colors.END}")
        print("• Messages are sent via WhatsApp Web")
        print("• Keep browser window open during sending")
        print("• Schedule at least 1-2 minutes in the future")
        print("• Test with your own number first\n")
        input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def get_phone_number(self) -> Optional[str]:
        print(f"\n{Colors.BOLD}Select recipient:{Colors.END}")
        print(f"{Colors.BLUE}1.{Colors.END} Enter phone number manually")
        print(f"{Colors.BLUE}2.{Colors.END} Select from contacts")
        choice = input(f"\n{Colors.CYAN}Choice: {Colors.END}").strip()
        if choice == '1':
            phone = input(f"Phone (with country code, e.g., {self.preferences['country_code']}1234567890): ").strip()
            if not phone.startswith('+'):
                phone = self.preferences['country_code'] + phone
            return phone
        elif choice == '2':
            if not self.contacts:
                print(f"{Colors.YELLOW}No contacts saved{Colors.END}")
                return None
            self.view_contacts()
            name = input(f"\n{Colors.CYAN}Enter contact name: {Colors.END}").strip()
            return self.contacts.get(name)
        return None
    
    def get_schedule_time(self) -> tuple:
        print(f"\n{Colors.BOLD}Schedule Message:{Colors.END}")
        now = datetime.now()
        print(f"Current time: {Colors.GREEN}{now.strftime('%H:%M')}{Colors.END}")
        print(f"{Colors.BLUE}1.{Colors.END} Send in X minutes")
        print(f"{Colors.BLUE}2.{Colors.END} Specify exact time (24-hour format)")
        choice = input(f"\n{Colors.CYAN}Choice: {Colors.END}").strip()
        if choice == '1':
            minutes = input("Minutes from now (recommended: 1-5): ").strip()
            if minutes.isdigit():
                send_time = now + timedelta(minutes=int(minutes))
                return send_time.hour, send_time.minute
        elif choice == '2':
            hour = input("Hour (0-23): ").strip()
            minute = input("Minute (0-59): ").strip()
            if hour.isdigit() and minute.isdigit():
                return int(hour), int(minute)
        return None, None
    
    def run(self):
        self.print_header()
        while True:
            self.print_menu()
            choice = input(f"{Colors.CYAN}Enter your choice: {Colors.END}").strip()
            if choice == '1':
                phone = self.get_phone_number()
                if not phone:
                    continue
                message = input(f"\n{Colors.CYAN}Enter message: {Colors.END}").strip()
                if not message:
                    print(f"{Colors.RED}✗ Message cannot be empty{Colors.END}")
                    continue
                hour, minute = self.get_schedule_time()
                if hour is not None and minute is not None:
                    self.send_message(phone, message, hour, minute)
            elif choice == '2':
                phone = self.get_phone_number()
                if not phone:
                    continue
                message = input(f"\n{Colors.CYAN}Enter message: {Colors.END}").strip()
                if not message:
                    print(f"{Colors.RED}✗ Message cannot be empty{Colors.END}")
                    continue
                confirm = input(f"\n{Colors.YELLOW}Send immediately? (yes/no): {Colors.END}").strip().lower()
                if confirm in ['yes', 'y']:
                    self.send_instant_message(phone, message)
            elif choice == '3':
                group_id = input(f"\n{Colors.CYAN}Enter Group ID: {Colors.END}").strip()
                message = input(f"{Colors.CYAN}Enter message: {Colors.END}").strip()
                if not group_id or not message:
                    print(f"{Colors.RED}✗ Group ID and message are required{Colors.END}")
                    continue
                hour, minute = self.get_schedule_time()
                if hour is not None and minute is not None:
                    self.send_group_message(group_id, message, hour, minute)
            elif choice == '4':
                self.manage_contacts_menu()
            elif choice == '5':
                self.view_history()
            elif choice == '6':
                self.configure_preferences()
            elif choice == '7':
                self.setup_chrome_driver()
            elif choice == '8':
                self.test_connection()
            elif choice == '9':
                self.show_help()
            elif choice == '0':
                print(f"\n{Colors.GREEN}Thank you for using WhatsApp Automation CLI!{Colors.END}")
                print(f"{Colors.CYAN}Goodbye! 👋{Colors.END}\n")
                sys.exit(0)
            else:
                print(f"{Colors.RED}✗ Invalid choice. Please try again.{Colors.END}")

def main():
    try:
        app = WhatsAppAutomation()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Application interrupted by user{Colors.END}")
        print(f"{Colors.CYAN}Goodbye! 👋{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}✗ Fatal error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
