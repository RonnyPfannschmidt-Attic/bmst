from __future__ import print_function
import argparse
import shlex
import py

parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
parser.convert_arg_line_to_args = shlex.split

parser.add_argument('-s', '--store', required=True)
parser.add_argument('-d', '--debug', action='store_true')
parser.add_argument('-c', '--check', action='store_true')
parser.add_argument('--backup', default=[], action='append')
parser.add_argument('--serve', action='store_true')


from bmst.backup_app import make_backup
from bmst.managed import BMST, check_bmst
from bmst.store import FileStore, Httplib2Store


def main():
    opts = parser.parse_args()
    if opts.debug:
        print(opts)
    print('using store', opts.store)
    bmst = get_bmst(opts.store)

    if opts.check:
        check_bmst(bmst)

    for to_backup in opts.backup:
        path = py.path.local(to_backup)
        make_backup(root=path, bmst=bmst)

    if opts.serve:
        from bmst.wsgi import app
        app.bmst = bmst
        app.run()


def get_bmst(path):
    if path.startswith('http'):
        path = path.rstrip('/')
        blobs = Httplib2Store(path + '/blobs/')
        meta = Httplib2Store(path + '/meta/')
    else:
        root = py.path.local(path)
        root.ensure(dir=1)
        meta = FileStore(root.ensure('meta', dir=1))
        blobs = FileStore(root.ensure('blobs', dir=1))
    return BMST(meta=meta, blobs=blobs)
