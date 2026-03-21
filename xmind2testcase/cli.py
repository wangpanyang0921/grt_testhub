#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import logging
import sys
from xmind2testcase.xlsx import xmind_to_xlsx_file
from xmind2testcase.utils import get_absolute_path
from webtool.application import launch

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(name)s  %(levelname)s  [%(module)s - %(funcName)s]: %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

using_doc = """
    Xmind2Testcase is a tool to parse xmind file into testcase file, which will help you generate Excel xlsx file.
    
    Usage:
     xmind2testcase [path_to_xmind_file] [-xlsx]
     xmind2testcase [webtool] [port_num]
    
    Example:
     xmind2testcase /path/to/testcase.xmind        => output testcase.xlsx
     xmind2testcase /path/to/testcase.xmind -xlsx  => output testcase.xlsx
     xmind2testcase webtool                        => launch the web testcase conversion tool locally: 127.0.0.1:5001
     xmind2testcase webtool 8000                   => launch the web testcase conversion tool locally: 127.0.0.1:8000
    """


def cli_main():
    if len(sys.argv) > 1 and sys.argv[1].endswith('.xmind'):
        xmind_file = sys.argv[1]
        xmind_file = get_absolute_path(xmind_file)
        logging.info('Start to convert XMind file: %s', xmind_file)

        if len(sys.argv) == 3 and sys.argv[2] == '-xlsx':
            xlsx_file = xmind_to_xlsx_file(xmind_file)
            logging.info('Convert XMind file to xlsx file successfully: %s', xlsx_file)
        else:
            xlsx_file = xmind_to_xlsx_file(xmind_file)
            logging.info('Convert XMind file successfully: xlsx file(%s)', xlsx_file)
    elif len(sys.argv) > 1 and sys.argv[1] == 'webtool':
        if len(sys.argv) == 3:
            try:
                port = int(sys.argv[2])
                launch(port=port)
            except ValueError:
                launch()
        else:
            launch()

    else:
        print(using_doc)


if __name__ == '__main__':
    cli_main()
