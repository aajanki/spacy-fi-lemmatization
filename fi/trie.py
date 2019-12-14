# coding: utf8
from __future__ import unicode_literals


class TrieNode(object):
    def __init__(self):
        self.children = {}
        self.values = []


class Trie(object):
    """Trie is a data structure for associating values with string prefixes."""

    def __init__(self):
        self.root = TrieNode()

    def find(self, key):
        """Find values associated with key and its prefixes."""
        node = self.root
        values = list(node.values)
        for char in key:
            node = node.children.get(char)
            if node is None:
                break

            values.extend(node.values)

        return values

    def insert(self, key, value):
        """Asociate a value to a key.

        Multiple values can be associated with a key.
        """

        node = self.root
        for char in key:
            node = node.children.setdefault(char, TrieNode())

        node.values.append(value)
