"""Скрипт для сборки игры в один автономный .exe файл."""
import subprocess
import sys


def build():
    # Запускаем PyInstaller с параметрами:
    # --onefile: упаковать всё в один .exe
    # --windowed: скрыть черную консоль при запуске окна
    # --name Chess: красивое имя исполняемого файла
    # --add-data: вкладываем картинки фигур
    # --exclude-module: исключаем тяжелые библиотеки (numpy, matplotlib и др.),
    # которые случайно цепляет Pillow, чтобы экзешник весил минимально
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'Chess',
        '--add-data', 'assets;assets',
        '--exclude-module', 'numpy',
        '--exclude-module', 'scipy',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'pandas',
        '--exclude-module', 'pygame',
        '--exclude-module', 'unittest',
        '--exclude-module', 'pydoc',
        '--exclude-module', 'sqlite3',
        '--exclude-module', 'ssl',
        '--exclude-module', 'asyncio',
        '--exclude-module', 'multiprocessing',
        '--exclude-module', 'email',
        '--exclude-module', 'http',
        '--exclude-module', 'xmlrpc',
        'run.py'
    ]
    print('Собираем исполняемый файл Chess.exe...')
    subprocess.run(cmd, check=True)
    print('\nГотово! Файл для релиза находится в: dist/Chess.exe')


if __name__ == '__main__':
    build()
