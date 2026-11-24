"""Скрипт для сборки игры в один автономный .exe файл."""
import subprocess
import sys


def build():
    # Запускаем PyInstaller с параметрами:
    # --onefile: упаковать всё в один .exe
    # --windowed: скрыть черную консоль при запуске окна
    # --name Chess: красивое имя исполняемого файла
    # --add-data: обязательно вкладываем картинки фигур
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'Chess',
        '--add-data', 'assets;assets',
        'run.py'
    ]
    print('Собираем исполняемый файл Chess.exe...')
    subprocess.run(cmd, check=True)
    print('\nГотово! Файл для релиза находится в: dist/Chess.exe')


if __name__ == '__main__':
    build()
