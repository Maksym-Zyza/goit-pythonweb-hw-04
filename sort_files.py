import argparse
import asyncio
from time import time

from aiopath import AsyncPath
from aioshutil import copyfile
from logger import logger


parser = argparse.ArgumentParser(description="Sorting folder async by file extensions")
parser.add_argument("--source", "-s", required=True, help="Source folder")
parser.add_argument("--output", "-o", default="dist", help="Output folder")
args = vars(parser.parse_args())

source_folder = AsyncPath(args.get("source"))
output_folder = AsyncPath(args.get("output"))


async def read_folder(path: AsyncPath) -> None:
    try:
        async for el in path.iterdir():
            if await el.is_dir():
                await read_folder(el)
            elif await el.is_file():
                await copy_file(el)
    except Exception as e:
        logger.error(f"Error while reading folder {path}: {e}")


async def copy_file(file: AsyncPath) -> None:
    try:
        ext = file.suffix[1:] if file.suffix else "no_extension"
        target_folder = output_folder / ext
        await target_folder.mkdir(parents=True, exist_ok=True)
        await copyfile(file, target_folder / file.name)
        logger.info(f"Copied {file} to {target_folder}")
    except Exception as e:
        logger.error(f"Error copying file {file}: {e}")


async def main():
    if not await source_folder.exists():
        logger.error(f"Source folder '{source_folder}' does not exist.")
        return
    await output_folder.mkdir(parents=True, exist_ok=True)

    await read_folder(source_folder)


if __name__ == "__main__":
    start = time()
    asyncio.run(main())
    print(f"Completed in: {time() - start:.2f} seconds")
