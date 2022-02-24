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
        orig = ZipFile(path / Path("orig.zip"), "a")
        orig.close