import subprocess


def checkout_positive(cmd, text):
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, encoding="utf-8")
    if result.returncode == 0 and text in result.stdout:
        return True
    else:
        return False


def checkout_negative(cmd, text):
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    if result.returncode != 0 and (text in result.stderr or text in result.stdout):
        return True
    else:
        return False


def getout(folder: str, archive: str) -> str:
    sb = subprocess.run(f"cd {folder}; crc32 {archive}", shell=True, stdout=subprocess.PIPE, encoding='utf-8')
    return sb.stdout[:-1].upper()