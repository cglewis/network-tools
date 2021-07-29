"""
Test module for tcpdump_hex_parser.py

Created on 13 June 2016
@author: Charlie Lewis
"""

import pytest
import re
import sys

from .tcpdump_hex_parser import get_path
from .tcpdump_hex_parser import parse_header
from .tcpdump_hex_parser import parse_data
from .tcpdump_hex_parser import return_packet
from .tcpdump_hex_parser import run_tool

def test_get_path():
    get_path()
    sys.argv = []
    get_path()

def test_run_tool():
    with open('/tmp/test', 'w') as f:
        f.write("this is a test file")
    run_tool('/tmp/test')

def test_parse_header():
    ret_dict = parse_header("2015-05-20 12:41:45.812393 IP 0.0.0.0 > 0.0.0.0: ESP(spi=0xb1ced15c,seq=0x30), length 184")
    assert isinstance(ret_dict, dict)
    assert ret_dict['date'] == "2015-05-20"
    assert ret_dict['time'] == "12:41:45.812393"
    assert ret_dict['raw_header'] == "2015-05-20 12:41:45.812393 IP 0.0.0.0 > 0.0.0.0: ESP(spi=0xb1ced15c,seq=0x30), length 184"
    assert ret_dict['ethernet_type'] == "IP"
    assert ret_dict['src_ip'] == "0.0.0.0"
    assert ret_dict['dest_ip'] == "0.0.0.0"
    assert ret_dict['protocol'] == "ESP(spi=0xb1ced15c,seq=0x30),"
    assert ret_dict['length'] == 184

    ret_dict = parse_header("2015-05-20 12:41:45.812393 IP 0.0.0.0.80 > 0.0.0.0.80: ESP(spi=0xb1ced15c,seq=0x30), length 184")
    assert ret_dict['src_ip'] == "0.0.0.0"
    assert ret_dict['dest_ip'] == "0.0.0.0"
    assert ret_dict['src_port'] == "80"
    assert ret_dict['dest_port'] == "80"

    ret_dict = parse_header("2015-05-20 12:41:45.812393 IP 0.0.0.0.80 > 0.0.0.0.80: ESP(spi=0xb1ced15c,seq=0x30)")
    assert ret_dict['src_ip'] == "0.0.0.0"
    assert ret_dict['dest_ip'] == "0.0.0.0"
    assert ret_dict['src_port'] == "80"
    assert ret_dict['dest_port'] == "80"
    assert ret_dict['length'] == 0

def test_parse_data():
    ret_str = parse_data("\t0x0080:  e04b 2935 564f 91db 5344 5460 9189 33d0", 0)
    assert isinstance(ret_str, str)
    hex_pattern = re.compile(r'[0-9a-fA-F]+')
    m = re.search(hex_pattern, ret_str)
    assert m

def test_return_packet():
    lines = []
    lines.append("2015-05-20 12:41:45.812393 IP 0.0.0.0 > 0.0.0.0: ESP(spi=0xb1ced15c,seq=0x30), length 0")
    lines.append("\t0x0080:  e04b 2935 564f 91db 5344 5460 9189 33d0")
    lines.append("2015-05-20 12:41:45.812393 IP 0.0.0.0 > 0.0.0.0: ESP(spi=0xb1ced15c,seq=0x30), length 0")
    lines.append("\t0x0080:  e04b 2935 564f 91db 5344 5460 9189 33d0")
    packets = return_packet([line.encode('utf-8') for line in lines])
    for packet in packets:
        assert isinstance(packet, dict)
        assert packet['data'] == "e04b2935564f91db53445460918933d0"
        assert packet['raw_header'] == "2015-05-20 12:41:45.812393 IP 0.0.0.0 > 0.0.0.0: ESP(spi=0xb1ced15c,seq=0x30), length 0"
        assert packet['date'] == "2015-05-20"
        assert packet['time'] == "12:41:45.812393"
