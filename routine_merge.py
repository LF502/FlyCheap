from zipfile import ZipFile
from pathlib import Path
from datetime import date
import pandas

if __name__ == "__main__":
    
    curr = date.today().isoformat()
    paths = []
    for path in Path().iterdir():
        if path.is_dir():
            path = path / Path(curr)
            if path.exists():
                paths.append(path)
        elif path.is_file():
            if path.suffix == '.csv' and curr in path.stem and 'merging' in path.stem:
                file = Path('merged_' + path.stem.split('_', 4)[1] + '.csv')
                if file.exists():
                    pandas.read_csv(path).to_csv(file, mode = 'a', index = False, header = False)
                else:
                    pandas.read_csv(path).to_csv(file, index = False)
    
    for path in paths:
        orig_folder = path / Path(".orig")
        if not orig_folder.exists():
            orig_folder.mkdir()
        orig = ZipFile(path / Path("orig.zip"), "a")
        for file in path.iterdir():
            if file.suffix == '.xlsx' and '_preproc' not in file.stem:
                orig.write(file, file.name)
                file.replace(orig_folder / Path(file.name))
        orig.close