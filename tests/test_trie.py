# coding: utf-8
from __future__ import unicode_literals

import pytest
from fi.trie import Trie


def test_trie():
    trie = Trie()
    trie.insert('abc', 1)
    trie.insert('def', 2)

    assert trie.find('abc') == [1]
    assert trie.find('def') == [2]
    assert trie.find('ab') == []
    assert trie.find('bc') == []
    assert trie.find('') == []

def test_trie_empty_key():
    trie = Trie()
    trie.insert('', 1)
    trie.insert('ab', 2)

    assert trie.find('') == [1]
    assert trie.find('a') == [1]
    assert trie.find('ab') == [1, 2]
    assert trie.find('abc') == [1, 2]


def test_find_prefix():
    trie = Trie()
    trie.insert('abc', 1)

    assert trie.find('abc') == [1]
    assert trie.find('abcd') == [1]


def test_trie_find_all_prefixes():
    trie = Trie()
    trie.insert('abc', 1)
    trie.insert('abcd', 2)
    trie.insert('abcdef', 3)

    assert trie.find('abcd') == [1, 2]
    assert trie.find('abcdefg') == [1, 2, 3]
