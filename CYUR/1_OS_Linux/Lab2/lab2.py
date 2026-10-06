import os
import pathlib
import random
import string
import shutil
import tarfile

NAME_LEN = 5
MAX_DEPTH = 3
MAX_WIDTH = 3
random_choice = [True, False]


def generate_name():
    name = random.choices(string.digits + string.ascii_letters,
                          k=NAME_LEN)
    name = ''.join(name)
    return name


def make_dir(name):
    path = pathlib.Path.cwd().joinpath(name)
    path.mkdir(parents=True, exist_ok=True)


def generate_nested(depth=1, max_width=MAX_WIDTH, max_depth=MAX_DEPTH):
    start = 2 if depth == 1 else 1
    number = random.randrange(start, max_width)
    for i in range(number):
        name = generate_name()
        make_dir(name)
        os.chdir(f'./{name}')
        if depth >= max_depth:
            if random.choice(random_choice):
                secret = generate_name()
                with open(secret, 'w') as f:
                    f.write(secret)
                random_choice.remove(True)
            os.chdir('..')
        else:

            depth = generate_nested(depth + 1)
    os.chdir('..')
    return depth - 1


def generate_text_struct():
    print('Task 2')
    print('Replicate the directory structure below with terminal commands ')
    print('The structure is:')
    name = generate_name()
    make_dir(name)
    startpath = f'./{name}'
    os.chdir(startpath)
    generate_nested()
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = '    |' * (level) + '└———' if level != 0 else ''
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = '|———' * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))
    shutil.rmtree(startpath)
    print('\n\n')


def generate_dirs():
    name = generate_name()
    make_dir(name)
    os.chdir(f'./{name}')
    generate_nested()
    print('Task 1')
    print('Investigate a nested directory and draw its structure')
    print(f'Your task directory is "{name}"!')
    print('Good luck!\n\n')


def generate_archive():
    cite = ['Отвлекись от всего, Нео! ',
            'Следуй за белым кроликом.',
            'Матрица повсюду. Она окружает нас.',
            'Ты только раб, Нео. Как и все, ты с рождения в цепях.',
            'Ты веришь в судьбу, Нео?',
            'Ложки не существует.',
            'Продам гараж!']

    with open('secret_file', 'w') as f:
        f.write(random.choice(cite))

    archive_name = 'task3.tar.gz'
    tar = tarfile.open(archive_name, 'w:gz')
    for name in ['secret_file']:
        tar.add(name)
    tar.close()

    os.remove('secret_file')

    print('Task 3')
    print(f'You have to extract the archive {archive_name}')
    print('and find a secret text.')


if __name__ == '__main__':
    generate_dirs()
    generate_text_struct()
    generate_archive()
