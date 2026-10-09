"""
HTML reader for the accessibility gates, in one place.

The a11y.py files measure the HTML the site emits. To do that, they build a
simple tree with the standard library's HTMLParser: each node is a dict with
tag, attrs, kids (children), text (direct text), line (line in the file) and
parent.

    t = Tree(); t.feed(html)      builds the tree; the root is t.root
    walk(node)                    every descendant, in document order
    classes(node) / has(node, c)  the node's classes / whether it has a class
    ancestors(node)               parents, nearest to farthest (without the root)
    text_of(node)                 text of the node and its children, trimmed
    text_flat(node)               the same, with all repeated whitespace collapsed

What stays out of the tree: the content of <style> and <script> (not markup).
<template> goes in by default, because that is where the markup the JS inserts
later lives (Toast, Alert). Whoever doesn't want the template samples passes
Tree(skip=SKIP_TEMPLATE).
"""
from html.parser import HTMLParser

# Void elements: they never have children, so they don't go on the stack.
VOID = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
    'meta', 'source', 'track', 'wbr',
    # SVG shapes: on the site they always come self-closed (<path ... />), but a
    # <path> without the slash must not swallow its siblings
    'path', 'circle', 'line', 'rect', 'polyline', 'polygon', 'ellipse',
}

SKIP = ('style', 'script')
SKIP_TEMPLATE = ('style', 'script', 'template')


class Tree(HTMLParser):
    def __init__(self, skip=SKIP):
        super().__init__(convert_charrefs=True)
        self.root = {'tag': '#root', 'attrs': {}, 'kids': [], 'text': '', 'line': 0}
        self.stack = [self.root]
        self.skip_tags = skip
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip += 1
            return
        if self.skip:
            return
        node = {'tag': tag, 'attrs': dict((k, v or '') for k, v in attrs),
                'kids': [], 'text': '', 'line': self.getpos()[0], 'parent': self.stack[-1]}
        self.stack[-1]['kids'].append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and not self.skip and self.stack[-1]['tag'] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip or tag in VOID:
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if not self.skip:
            self.stack[-1]['text'] += data


def walk(node):
    for k in node['kids']:
        yield k
        yield from walk(k)


def classes(node):
    return node['attrs'].get('class', '').split()


def has(node, cls):
    return cls in classes(node)


def ancestors(node):
    p = node.get('parent')
    while p is not None and p['tag'] != '#root':
        yield p
        p = p.get('parent')


def text_of(node):
    return (node['text'] + ''.join(text_of(k) for k in node['kids'])).strip()


def text_flat(node):
    return ' '.join((node['text'] + ' ' + ' '.join(text_flat(k) for k in node['kids'])).split())
