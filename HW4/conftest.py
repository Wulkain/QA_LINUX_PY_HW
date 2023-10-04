import random
import string
import pytest
import yaml

from sshcheckers import ssh_checkout, ssh_getout
from checkout import checkout_positive

with open("config.yaml") as f:
    data = yaml.safe_load(f)


@pytest.fixture()
def make_folders():
    return ssh_checkout(data["host"], data["user"], "123",
                        f'mkdir {data["folder_in"]} {data["folder_out"]} {data["folder_ext"]} {data["folder_badarx"]}',
                        "")


@pytest.fixture()
def clear_folders():
    return ssh_checkout(data["host"], data["user"], "123",
                        f'rm -rf {data["folder_in"]}/* {data["folder_out"]}/* {data["folder_ext"]}/* '
                        f'{data["folder_badarx"]}/*',
                        "")


@pytest.fixture()
def make_files():
    list_off_files = []
    for i in range(data["count_file"]):
        filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if ssh_checkout(data["host"], data["user"], "123",
                        f'cd {data["folder_in"]}; '
                        f'dd if=/dev/urandom of={filename} bs={data["size_file"]} count=1 iflag=fullblock',
                        ''):
            list_off_files.append(filename)
    return list_off_files


@pytest.fixture()
def make_subfolder():
    testfilename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    subfoldername = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    if not ssh_checkout(data["host"], data["user"], "123",
                        f'cd {data["folder_in"]}; mkdir {subfoldername}',
                        ''):
        return None, None
    if not ssh_checkout(data["host"], data["user"], "123",
                        f'cd {data["folder_in"]}/{subfoldername}; '
                        f'dd if=/dev/urandom of={testfilename} bs=1M count=1 iflag=fullblock',
                        ""):
        return subfoldername, None
    else:
        return subfoldername, testfilename


@pytest.fixture()
def make_bad_arx():
    """Написать фикстуру, создающую перед шагом теста битый архив
    и удаляющую его после завершения шага теста."""
    ssh_checkout(data["host"], data["user"], "123",
                 f'cd {data["folder_in"]}; '
                 f'7z a -t{data["arc_type"]} {data["folder_badarx"]}/badarx.{data["arc_type"]}',
                 "")
    ssh_checkout(data["host"], data["user"], "123",
                 f'truncate -s 1 {data["folder_badarx"]}/badarx.{data["arc_type"]}',
                 "")
    yield
    ssh_checkout(data["host"], data["user"], "123",
                 f'rm -f {data["folder_badarx"]}/badarx.{data["arc_type"]}',
                 "")


@pytest.fixture(autouse=True)
def write_stat():
    if not checkout_positive(f'ls {data["local_path"]}',
                             data["stat_file"]):
        checkout_positive(f'echo > "{data["local_path"]}/{data["stat_file"]}"; ls {data["local_path"]}',
                          data["stat_file"])

    with open(f'{data["local_path"]}/{data["stat_file"]}', 'w', encoding='utf-8') as f_stat:
        f_stat.write(ssh_getout(data["host"], data["user"], "123",
                                f'journalctl --since today'))