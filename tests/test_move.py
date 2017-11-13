import pytest
import boto3
from click.testing import CliRunner
from s3mover import move
from random import randint


@pytest.fixture
def runner():
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
    result = runner.invoke(move.main, ['X', 'y'])
    assert result.exit_code == 2
    assert result.exception
    assert 'Invalid value for "src": Path "X" does not exist' in str(result.output)


def test_cli_good_path_bad_bucket(runner):
    result = runner.invoke(move.main, ['./setup.cfg', 'y'])
    assert result.exit_code == -1
    assert result.exception
    assert 'specified bucket is not valid' in str(result.exception)


def test_cli_good_path_good_bucket(runner):
    client = boto3.client('s3')
    id = 'xtb{0}'.format(randint(1000, 9999))
    cbc = {'LocationConstraint': 'us-west-2'}
    client.create_bucket(Bucket=id, CreateBucketConfiguration=cbc)
    result = runner.invoke(move.main, ['./setup.cfg', id])
    assert result.exit_code == 0
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(id)
    for s3_file in bucket.objects.all():
        s3_file.delete()
    bucket.delete()

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
