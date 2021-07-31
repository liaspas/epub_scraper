# epub_scraper

A simple scirpt to extract, clean and format .epub text.  
Paragraphs are separated with a single line break `\n`, and chapters with a chapter break `***`.  
Curly quotes are replaced with straight quotes, and unicode `…` with `...`

Run with:
```
python3 epub_scraper.py -i {input_dir} -o {output_dir}
```

If not specified, the script will look for .epub files in a folder `./input` and output the .txt files to `./output`.
