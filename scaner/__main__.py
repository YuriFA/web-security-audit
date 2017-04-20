#!/usr/bin/env python

# Execute with
# $ python scaner/__main__.py (2.6+)
# $ python -m scaner          (2.7+)

import sys

if __package__ is None and not hasattr(sys, "frozen"):
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(path)))

import scaner

if __name__ == '__main__':
    scaner.main()