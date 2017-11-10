import click
from pathlib import Path
import boto3
import botocore
from botocore.exceptions import ClientError
import os

@click.command()
@click.option('--debug/--no-debug', '-d', default=False, help='Debug mode')
@click.option('--tag','-t', nargs=2, multiple=True)
@click.option('--delete/--no-delete', '-x', default=False, help='Delete files that get copied')
@click.option('--region', required=False, help='Override of default region')
@click.argument('src', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True, allow_dash=False),required=True)
@click.argument('bucket',required=True)
def main(debug,src,bucket, tag, delete, region):
    """Move a file at a given path to an S3 bucket"""
    path = Path(src)
    if path.exists():
        print bucket
        if debug: click.echo('{0} exists, tags = "{1}"'.format(src,(tag)))
        my_bucket = get_bucket(bucket, region)
        if debug: click.echo('Got bucket resource {0}'.format(bucket)) if my_bucket else click.echo("NO BUCKET")
        if my_bucket:
            try:
                s3_client = boto3.client('s3', region_name=region)
                # Upload the file to S3
                s3_client.upload_file(src, bucket, path.name)
                if delete:
                    key = s3_client.head_object(Bucket=bucket,Key=path.name)
                    if not key['ContentLength'] == path.stat().st_size:
                        print "Bucket object not same size"
                    else:
                        path.unlink()

            except ClientError as e:
                click.fail(e.msg)
    else:
        print '{0} does not exist'.format(src)

def get_bucket(candidate, region):
    """Get a bucket if it exists"""
    s3 =  boto3.resource('s3', region_name=region)
    exists = True
    try:
        s3.meta.client.head_bucket(Bucket=candidate)
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            exists = False
    return s3.Bucket(candidate) if exists else None
