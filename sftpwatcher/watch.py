import click
import psutil
from pathlib import Path
import re
import shutil
import subprocess
import os


@click.command()
@click.option('--debug', '-d', is_flag=True, help='Debug mode')
@click.option('--executable', default='echo', help='Executable to run with the file as a parameter')
@click.option('--matches', default='.*', help='Regex for files to match')
@click.option('--files', is_flag=True, default=True, help='Only check files, not directories')
@click.option('--relocate', type=click.Path(exists=True, dir_okay=True, readable=True, writable=True,
              resolve_path=True, allow_dash=False), help='Directory to relocate file to first')
@click.argument('path', type=click.Path(exists=True, dir_okay=True, readable=True,
                resolve_path=True, allow_dash=False), required=True)
def main(debug, path, relocate, executable, matches, files):
    """Watch a directory and do stuff to matching files there once nothing has them open"""
    if not Path(executable).exists():
        click.echo("Warning: {0} is not necessarily a file".format(executable))
    da_paths = [pth for pth in Path(path).iterdir()
                if (not files or (pth.is_file() and files))
                and (re.search(matches, str(pth.name)) and no_handle(str(pth)))]
    with click.progressbar(da_paths) as pths:
        for oper in pths:
            if debug:
                rstr = ''
                if relocate:
                    pth = Path(relocate).resolve()
                    print "PATH = {0}".format(pth.as_posix())
                    rstr = ', after relocating to {0}'.format(pth.as_posix())
                click.echo('Run "{2} {0}{1}"'.format(oper, rstr, executable))
            workPath = relo_path(relocate, oper)
            process = subprocess.Popen([executable, workPath])
            print process


def relo_path(relocate, original):
    workPath = original
    if relocate:
        workPath = Path(relocate) / original.name
        shutil.move(original.as_posix(), workPath.as_posix())
    return workPath.as_posix()


def no_handle(the_path):
    for the_pid in psutil.process_iter():
        try:
            for file in the_pid.open_files():
                if the_path == file.path:
                    return False
        except Exception:
            pass

    return True
