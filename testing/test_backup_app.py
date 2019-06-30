import bz2
import json

import pytest

from bmst.backup_app import fullmeta
from bmst.backup_app import load_tree
from bmst.backup_app import make_backup
from bmst.managed import BMST
from bmst.store import FileStore
from bmst.managed import sha1

CONTENT = b"test\n"
CONTENT_HASH = sha1(CONTENT)


@pytest.fixture(params=[dict, FileStore])
def bmst(request):
    if request.param is dict:
        return BMST({}, {})
    pytest.skip("not implemented")


def test_load(tmp_path):
    assert load_tree(tmp_path) == ({}, 0)

    create = tmp_path / "a/b"
    create.parent.mkdir()
    create.write_bytes(CONTENT)

    assert load_tree(tmp_path) == (
        {"a/b": (CONTENT_HASH, CONTENT)},
        tmp_path.joinpath("a/b").stat().st_mtime,
    )


def test_fullmeta(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    root.joinpath("test").write_bytes(b"test\n")
    meta, blobs = fullmeta(root)
    assert meta == {
        "project": "root",
        "tags": ["backup"],
        "timestamp": meta["timestamp"],  # steal timestamp
        "items": {"test": CONTENT_HASH},
    }

    assert blobs == {CONTENT_HASH: CONTENT}


def test_makebackup(tmp_path, bmst):
    test_fullmeta(tmp_path)
    make_backup(tmp_path / "root", bmst)
    assert bmst.blobs == {
        CONTENT_HASH: (
            b"BZh91AY&SY\xcc\xc3q\xd4\x00\x00\x02A\x80\x00\x10\x02\x00\x0c\x00"
            b' \x00!\x9ah3M\x19\x97\x8b\xb9"\x9c(Hfa\xb8\xea\x00'
        )
    }
    key, = bmst.meta.keys()
    data = bz2.decompress(bmst.meta[key])
    meta = json.loads(data)
    assert meta == {
        "project": "root",
        "tags": ["backup"],
        "timestamp": meta["timestamp"],  # steal timestamp
        "items": {"test": CONTENT_HASH},
    }
