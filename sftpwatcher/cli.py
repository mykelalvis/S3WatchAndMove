import click
import psutil


@click.command()
@click.option('--debug', '-d', is_flag=True, help='Debug mode')
@click.argument('--path', '-p', required=True, help='Directoy to monitor')
@clich.option('--relocate', '-r', is_flag=True, required=False, default=False, help='Move files before running executable')
@click.argument('--executable', '-e', default='echo', required=False, help='Executable to run on each file.  Passes full path of file as only parameter.')
def main(debug,path,relocate,executable):
    """Watch SFTP and do stuff to a dir of files once it no longer has them open"""
    greet = 'Howdy' if debug else 'Hello'
    rel = 'relocated' if relocate else 'NOT relocated'
    click.echo('{0}.  Run for {1}, {2}, executing "{3}" '.format(greet, sftp, path, rel, executable))

def has_handle(the_path):
    for the_pid in psutil.process_iter():
        try:
            for file in the_pid.open_files():
                if the_path == file.path:
                    return True
        except Exception:
            pass

    return False
