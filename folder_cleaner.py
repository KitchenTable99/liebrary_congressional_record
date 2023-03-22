import os
from glob import glob


def main():
    subdirs = glob('./**/', recursive=True)
    for subdir in subdirs:
        if 'pdf' in subdir or 'html' in subdir:
            pdfglob = glob(f'{subdir}/*')
            for file in pdfglob:
                os.remove(file)

    files = glob('./*/**', recursive=True)
    for file in files:
        if '.xml' in file:
            os.remove(file)


if __name__ == "__main__":
    main()
