import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import argparse
import glob
import os
import re

# this might vary in each book
div_classes_to_include = ["p", re.compile("p-indent(\d)*"), re.compile("calibre(\d)*")]


def epub2thtml(epub_path):
    """Extracts chapters from .epub file.
    """
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters


def chap2text(chap):
    """Extracts the text of a chapter.
    """
    output = ''
    soup = BeautifulSoup(chap, 'html.parser')
    text = [el.get_text() for el in soup.find_all("div", div_classes_to_include)]

    # some don't use div, and we have to fliter paragraphs
    text += [el.get_text() for el in soup.find_all("p") if not el.find(class_="bold")]
    for t in text:
        output += f'{t}\n'

    return output


def clean_text(text):
    """Final pass to clean and format the chapter text.
    """
    # for some reason this should be whitespace. NOTE: Might differ from book to book.
    text = re.sub(r"\r\n", ' ', text)
    # replace multiple whitesplaces with one
    text = re.sub(r"[^\S\r\n]+", ' ', text)

    # split by paragraph, removing trailing and leading whitespaces and myltiple newlines
    paragraphs = [p.strip() for p in text.split('\n') if p != '']
    # rejoin them, with only a \n separating each
    text = '\n'.join(paragraphs)

    # replace some symbols with more conventional ones
    text = re.sub(r"[“”]", "\"", text)
    text = re.sub(r"’", "'", text)
    text = re.sub(r" ?…", "...", text)
    text = re.sub(r"\* \* \*", "***", text)

    return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=False, default="./input", help="Directory containing the .epub files.")
    parser.add_argument("--out", "-o", required=False, default="./output", help="Output directory. If not spcified, output is writen to stdout.")
    args = parser.parse_args()

    # dictionary to hold the text per book (eg. {"book1": "...", "book2": "..."})
    final_book_texts = {}

    for file in sorted(glob.glob(os.path.join(args.input, "*.epub"))):
        chapters = epub2thtml(file)
        chapter_texts = [chap2text(ch) for ch in chapters]
        clean_chapter_texts = [clean_text(ch) for ch in chapter_texts if ch != '']
        final_book_texts[os.path.splitext(os.path.basename(file))[0]] = clean_chapter_texts

    os.makedirs(args.out, exist_ok=True)

    for book in final_book_texts.keys():
        with open(os.path.join(args.out, f"{book}.txt"), "w+") as f:
            for i, chapter in enumerate(final_book_texts[book]):
                f.write(chapter)
                # add chapter breaks
                f.write('\n***\n')
