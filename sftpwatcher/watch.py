import click
import psutil
from pathlib import Path
import re
import shutil
import subprocess


@click.command()
@click.option('--debug', '-d', is_flag=True, help='Debug mode')
@click.option('--executable', default='echo', help='Executable to run with the file as a parameter')
@click.option('--matches', default='.*', help='Regex for files to match')
@click.option('--relocate', type=click.Path(exists=True, dir_okay=True, readable=True, writable=True,
              resolve_path=True, allow_dash=False), help='Directory to relocate file to first')
@click.argument('path', type=click.Path(exists=True, dir_okay=True, readable=True,
                resolve_path=True, allow_dash=False), required=True)
def main(debug, path, relocate, executable, matches):
    """Watch a directory and do stuff to matching files there once nothing has them open"""
    rstr = '' if not relocate else ', after relocating to {0}'.format(Path(relocate).as_posix())

    if not Path(executable).exists():
        click.echo("Warning: {0} is not necessarily a file".format(executable))

    pths = [pth for pth in Path(path).iterdir() if re.search(matches, pth.name) and no_handle(pth)]
    for oper in pths:
        if debug:
            click.echo('Run "{2} {0}{1}"'.format(oper.as_posix(), rstr, executable))
        workPath = relo_path(relocate, oper)
        subprocess.Popen([executable, workPath])


def relo_path(rel, original):
    workPath = original
    if rel:
        workPath = Path(rel) / original.name
        shutil.move(original.as_posix(), workPath.as_posix())
    return workPath.as_posix()


def no_handle(the_path):
    for the_pid in psutil.process_iter():
        try:
            for file in the_pid.open_files():
                if file.path == the_path.as_posix():
                    return False
        except Exception:
            pass

    return True
