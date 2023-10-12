import subprocess

# Задайте путь к вашему локальному репозиторию
local_repo_path = "./"

# Выполнить git pull для обновления проекта
try:
    # Используем subprocess для выполнения команды git pull
    subprocess.run(["git", "pull"], cwd=local_repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    print("Проект успешно обновлен из GitHub.")
except subprocess.CalledProcessError as e:
    print("Ошибка при обновлении проекта:")
    print(e.stderr.decode('utf-8'))
except Exception as e:
    print("Ошибка:")
    print(str(e))
