import json
import re
import asyncio
try:
    from telethon.sync import TelegramClient
    from telethon import events
except ImportError:
    print("Telethon is not installed!\nPlease, install it by command: pip install telethon")
    exit()

class editor:

    app_id = 0
    app_hash = ""
    session = "./editmsgs_sf.session"

    commands = []

    client = None

    def __init__(self) -> None:
        self.opendict()

    def opendict(self, data: dict|list|None=[]) -> dict|list|None:
        result = []
        if len(data) == 0:
            try:
                with open("database.json", "r", encoding="utf-8") as file:
                    result = json.load(file)
            except Exception:
                result = []
        else:
            with open("database.json", "w+", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                result = data
        return result
        
    async def start_session(self) -> TelegramClient|None:
        print("[+] Session start... ok")
        try:
            client = TelegramClient(self.session, self.app_id, self.app_hash)
            await client.connect()
        except Exception as e:
            with open("log.txt", "w+", encoding="utf-8") as file:
                file.write(e)
            print("[-] Falied to connect to Telegram servers\nMore info in log.txt")
            exit()
        print("[+] Connection to Telegram servers... ok")
        self.client = client
        return client

    def get_command_list(self) -> str:
        commands_list = "Список доступных команд:\n"
        try:
            for command, replacements in self.commands.items():
                replacements_str = "\n    -> ".join(replacements)
                commands_list += f".{command}:\n    {replacements_str}\n\n"
        except Exception:
            commands_list += "  Команды не добавлены\n\n"
        commands_list += "Шпаргалка по командам:\n"\
                         "/add {команда} 'значение1','значение2','значение3' - добавление новой команды\n"\
                         "/del {команда} - удаление команды\n"\
                         "/listing - список всех комманд"
        return commands_list
    
    def delete_key(self, key: str) -> str:
        if key in self.commands:
            del self.commands[key]
            self.opendict(self.commands)
            print(f"[+] Deleting key :{key}... ok")
            return f"Команда :{key} успешно удалена"
        else:
            print(f"[-] Deleting key :{key}... Error `Key not found`")
            return f"Удаление команды :{key} не удалось, т.к. ее не существует, проверь доступные команды отправив /listing"
    
    def add_key(self, key: str, values: str) -> str:
        values_list = re.findall(r'["\'](.*?)["\']', values)
        self.commands[key] = values_list
        self.opendict(self.commands)
        for value in values_list:
            values_str = "\n    -> ".join(value)
        if key not in self.commands:
            print(f"[+] Add key :{key}... ok")
            return f"Добавлена новая команда :{key}"+values_str
        else:
            print(f"[-] Add key :{key}... Key updated")
            return f"Команда :{key} успешно обновлена"+values_str
        
    async def replace_text(self, message_text: str, chat_id: int|str, message_id: int|str) -> None:
        for command, replacements in self.commands.items():
            if message_text.startswith(f".{command}"):
                await self.client.delete_messages(chat_id, message_id)
                msg = await self.client.send_message(chat_id, replacements[0])
                for replacement in replacements[1:]:
                    msg = await self.client.edit_message(msg, text=replacement)
                    await asyncio.sleep(1.5)
    
if __name__ == "__main__":
    edit = editor()
    client = edit.start_session()
    
    @client.on(events.NewMessage(from_users=['me']))
    async def handler(event):
            msg = event.message
            if msg.text:
                if msg.text.startswith('.'):
                    await edit.replace_text(msg.text, msg.peer_id.user_id, msg.id)
                elif msg.text.startswith('/listing'):
                    await client.delete_message(msg)
                    await client.send_message(edit.get_command_list())
                elif msg.text.startswith('/add'):
                    parsed_msg = msg.text.split(" ", 2)
                    await client.delete_message(msg)
                    await client.send_message(edit.add_key(parsed_msg[1], parsed_msg[2]))
                elif msg.text.startswith('/del'):
                    parsed_msg = msg.text.split(" ")
                    await client.delete_message(msg)
                    await client.send_message(edit.delete_key(parsed_msg[1]))

    client.run_until_disconnected()
