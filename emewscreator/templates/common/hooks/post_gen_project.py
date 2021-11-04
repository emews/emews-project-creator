import os
import shutil


def run():
    to_remove = [os.path.join(os.getcwd(), "common")]
    for path in to_remove:
        shutil.rmtree(path)


if __name__ == '__main__':
    run()
