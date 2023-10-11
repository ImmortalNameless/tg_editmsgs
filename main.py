import json
import re
import asyncio
try:
    from telethon.sync import TelegramClient
    from telethon import events
    from telethon.errors.rpcerrorlist import MessageNotModifiedError
except ImportError:
    print("Telethon is not installed!\nPlease, install it by command: pip install telethon")
    exit()

app_id = 0
app_hash = ""
session = "./editmsgs_sf.session"

print("[+] Session start... ok")
try:
    client = TelegramClient(session, app_id, app_hash)
    client.start()
except Exception as e:
    with open("log.txt", "w+", encoding="utf-8") as file:
        file.write(e)
    print("[-] Falied to connect to Telegram servers\nMore info in log.txt")
    exit()


@client.on(events.NewMessage(from_users=['me']))
async def handler(event):
    global client
    edit = editor()
    edit.client = client
    msg = event.message
    if msg.text:
        if msg.text.startswith('.'):
            await edit.replace_text(msg.text, msg.peer_id.user_id, msg.id)
        elif msg.text.startswith('/listing'):
            await client.delete_messages(msg.peer_id.user_id, msg.id)
            await client.send_message(msg.peer_id.user_id, edit.get_command_list())
        elif msg.text.startswith('/add'):
            print(msg.text)
            parsed_msg = msg.text.split(" ", 2)
            print(parsed_msg)
            await client.delete_messages(msg.peer_id.user_id, msg.id)
            await client.send_message(msg.peer_id.user_id, edit.add_key(parsed_msg[1], parsed_msg[2]))
        elif msg.text.startswith('/del'):
            parsed_msg = msg.text.split(" ")
            await client.delete_messages(msg.peer_id.user_id, msg.id)
            await client.send_message(msg.peer_id.user_id, edit.delete_key(parsed_msg[1]))

class editor:

    commands = {}

    client = None

    def __init__(self) -> None:
        self.opendict()

    def opendict(self, data: dict|list|None={}) -> dict|list|None:
        result = {}
        if len(data) == 0:
            try:
                f = open("database.json", "r", encoding="utf-8")
                result = json.load(f)
                f.close()
            except Exception:
                result = {}
        else:
            f = open("database.json", "w+", encoding="utf-8")
            json.dump(data, f, ensure_ascii=False, indent=4)
            result = data
            f.close()
        self.commands = result
        return result

    def get_command_list(self) -> str:
        commands_list = "Список доступных команд:\n"
        try:
            for command, replacements in self.commands.items():
                replacements_str = "\n    -> ".join(replacements)
                commands_list += f".{command}:\n    -> {replacements_str}\n\n"
        except Exception:
            commands_list += "  Команды не добавлены\n\n"
        commands_list += "Шпаргалка по командам:\n"\
                         "/add {команда} 'значение1','значение2','значение3' - добавление новой команды\n"\
                         "/del {команда} - удаление команды\n"\
                         "/listing - список всех комманд"
        return commands_list
    
    def delete_key(self, key: str) -> str:
        if key in self.commands:
            new_commands = {}
            for k,v in self.commands.items():
                if k != key:
                    new_commands[k] = v
            self.opendict(new_commands)
            print(f"[+] Deleting key :{key}... ok")
            return f"Команда :{key} успешно удалена"
        else:
            print(f"[-] Deleting key :{key}... Error `Key not found`")
            return f"Удаление команды :{key} не удалось, т.к. ее не существует, проверь доступные команды отправив /listing"
    
    def add_key(self, key: str, values: str) -> str:
        values_list = re.findall(r'["\'](.*?)["\']', values)
        self.commands[f"{key}"] = values_list
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
                await asyncio.sleep(1.5)
                for replacement in replacements[1:]:
                    try:
                        await self.client.edit_message(chat_id, msg.id, text=replacement)
                    except MessageNotModifiedError:
                        await self.client.edit_message(chat_id, msg.id, text=replacements[replacements.index(replacement)])
                    await asyncio.sleep(1.5)

print("[+] Connection to Telegram servers... ok")
client.run_until_disconnected()