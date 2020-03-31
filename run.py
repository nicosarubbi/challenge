#!/usr/bin/env python3

import sys
from accounts import accounts, business_logic


if __name__ == '__main__':
    showinput = '--showinput' in sys.argv
    for line in sys.stdin:
        line = line.strip()
        operation = accounts.Operation.parse(line)
        if showinput:
            print('>>>', line)
        if operation:
            print(operation)

