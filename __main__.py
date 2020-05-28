import argparse

from bs4 import BeautifulSoup
import io
import requests
import json
from pathlib import Path
from tqdm import tqdm

from PIL import Image


def parse(url, saveto, resizeas=None, **kwargs):
    mainpage = BeautifulSoup( requests.get(url).text, features="lxml" )
    
    lis = mainpage.select('li.FnStickerPreviewItem')
    for i, li in tqdm(enumerate(lis), total=len(lis)):
        imgurl = json.loads( li.get('data-preview') )['staticUrl'].split(';')[0]
        imgbytes = requests.get(imgurl).content
        if resizeas <= 0:
            (saveto / f"{i:02d}.png").open('wb').write( imgbytes )
        else:
            img = Image.open(io.BytesIO(imgbytes))
            width, height = img.size
            if width == max(width, height):
                height = round( resizeas / width * height )
                width = resizeas
            else:
                width = round( resizeas / height * width )
                height = resizeas
            img.resize((width, height)).save( saveto / f"{i:02d}.png")




def main():
    parser = argparse.ArgumentParser(prog="")
    parser.add_argument('url', type=str)
    parser.add_argument('--saveto', type=Path)

    parser.add_argument('--resizeas', type=int, default=-1)
    parser.add_argument('--overwrite', action='store_true', default=False)

    args = parser.parse_args()

    if args.saveto is None:
        # infer from url
        args.saveto = Path(f"./{args.url.split('/')[5]}")

    if args.saveto.exists() and not args.overwrite:
        raise FileExistsError(f"{args.saveto} already exists")
    args.saveto.mkdir(parents=True, exist_ok=True)

    parse(**vars(args))

if __name__ == '__main__':
    main()