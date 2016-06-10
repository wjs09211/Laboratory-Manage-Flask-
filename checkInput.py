# encoding=utf8
import re


def check_regualr(m, str):
    if m is None:
        return False
    else:
        if m.group(0) == str:
            return True
        return False


def check_integer(str):
    m = re.search('^[1-9][0-9]*|^[0-9]$', str)
    return check_regualr(m, str)


def check_acc_pwd(str, num=4):
    if len(str) >= num:
        m = re.search('[a-zA-Z0-9]*', str)
        return check_regualr(m, str)
    else:
        return False


def check_email(str):
    m = re.search('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', str)
    return check_regualr(m, str)

print check_integer("")