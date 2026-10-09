"""
Leitor de HTML dos portoes de acessibilidade, num lugar so.

Os a11y.py medem o HTML que o site emite. Para isso, montam uma arvore simples
com o HTMLParser da biblioteca padrao: cada no e um dict com tag, attrs, kids
(filhos), text (texto direto), line (linha no arquivo) e parent.

    t = Tree(); t.feed(html)      monta a arvore; a raiz fica em t.root
    walk(no)                      todos os descendentes, em ordem de documento
    classes(no) / has(no, cls)    classes do no / se tem uma classe
    ancestors(no)                 pais, do mais perto ao mais longe (sem a raiz)
    text_of(no)                   texto do no e dos filhos, sem as pontas
    text_flat(no)                 o mesmo, com todo espaco repetido virando um so

O que fica de fora da arvore: o conteudo de <style> e <script> (nao e marcacao).
O <template> entra por padrao, porque e la que mora a marcacao que o JS insere
depois (Toast, Alert). Quem nao quer as amostras de template passa
Tree(skip=SKIP_TEMPLATE).
"""
from html.parser import HTMLParser

# Elementos sem fechamento: nunca tem filhos, entao nao entram na pilha.
VOID = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
    'meta', 'source', 'track', 'wbr',
    # formas do SVG: no site sempre vem fechadas (<path ... />), mas um <path>
    # sem a barra nao pode engolir os irmaos
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
