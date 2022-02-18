from zipfile import ZipFile
from pathlib import Path
from datetime import date

if __name__ == "__main__":
    
    paths = []
    for path in Path().iterdir():
        if path.is_dir():
            path = path / Path(date.today().isoformat())
            if path.exists():
                paths.append(path)
    
    for path in paths:
        orig_folder = path / Path(".orig")
        if not orig_folder.exists():
            orig_folder.mkdir()
        preproc_folder = path / Path(".preproc")
        if not preproc_folder.exists():
            preproc_folder.mkdir()
        orig = ZipFile(path / Path("orig.zip"), "a")
        preproc = ZipFile(path / Path("preproc.zip"), "a")
        for file in path.iterdir():
            if file.match('*_preproc.xlsx') or file.match('*_预处理.xlsx'):
                preproc.write(file, file.name)
                file.replace(preproc_folder / Path(file.name))
            elif file.match('*.xlsx'):
                orig.write(file, file.name)
                file.replace(orig_folder / Path(file.name))
        orig.close
        preproc.close