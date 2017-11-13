import pytest
import boto3
from click.testing import CliRunner
from s3mover import move
from random import randint
import os
import shutil

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if os.path.exists(directory):
        shutil.rmtree(file_path, True)
    shutil.copytree('src/test/resources/', file_path)
    return directory


@pytest.fixture
def runner():
    directory = ensure_dir('./target')
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(move.main)
    assert result.exit_code == 2
    assert result.exception
    assert 'Error: Missing argument' in str(result.output)


def test_cli_single_opt(runner):
    result = runner.invoke(move.main, ['X'])
    assert result.exit_code == 2
    assert result.exception
    assert 'Invalid value for "src": Path "X" does not exist' in str(result.output)


def test_cli_both_opts_bad_path(runner):
    result = runner.invoke(move.main, ['y','X'])
    assert result.exit_code == 2
    assert result.exception
    assert 'Invalid value for "src": Path "X" does not exist' in str(result.output)


def test_cli_good_path_bad_bucket(runner):
    result = runner.invoke(move.main, ['./target/testfile.txt', 'y'])
    assert result.exit_code == -1
    assert result.exception
    assert 'specified bucket is not valid' in str(result.exception)


def test_cli_good_path_good_bucket(runner):
    client = boto3.client('s3')
    id = 'xtb{0}'.format(randint(1000, 9999))
    cbc = {'LocationConstraint': 'us-west-2'}
    client.create_bucket(Bucket=id, CreateBucketConfiguration=cbc)
    result = runner.invoke(move.main, [id, './target/testfile.txt'])
    assert result.exit_code == 0
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(id)
    ass = False
    for s3_file in bucket.objects.all():
        ass = (s3_file.key == 'testfile.txt')

    for s3_file in bucket.objects.all():
        s3_file.delete()
    bucket.delete()

    assert ass

def test_cli_good_path_good_bucket(runner):
    client = boto3.client('s3')
    id = 'xtb{0}'.format(randint(1000, 9999))
    cbc = {'LocationConstraint': 'us-west-2'}
    client.create_bucket(Bucket=id, CreateBucketConfiguration=cbc)
    result = runner.invoke(move.main, [ '--delete', id, './target/testfile.txt'])
    assert result.exit_code == 0
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(id)
    ass = False
    for s3_file in bucket.objects.all():
        ass = (s3_file.key == 'testfile.txt')

    for s3_file in bucket.objects.all():
        s3_file.delete()
    bucket.delete()

    assert ass


# def test_cli_with_option(runner):
#     result=runner.invoke(cli.main, ['--as-cowboy'])
#     assert not result.exception
#     assert result.exit_code == 0
#     assert result.output.strip() == 'Howdy, world.'
#
#
# def test_cli_with_arg(runner):
#     result=runner.invoke(cli.main, ['Mykel'])
#     assert result.exit_code == 0
#     assert not result.exception
#     assert result.output.strip() == 'Hello, Mykel.'
