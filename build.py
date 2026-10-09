"""
Build completo do AL Design System, num comando so.

Roda, na ordem certa, todos os geradores e portoes: Foundation, tokens e CSS de
cada componente, o site e o QA de acessibilidade de cada componente. Para no
primeiro passo que falhar, e mostra a saida dele.

Rodar (da raiz do repo):
    python3 build.py            build completo
    python3 build.py --check    build completo e depois confere que nada mudou
                                em relacao ao que esta commitado (e o que o
                                GitHub Actions roda em cada PR)
    python3 build.py --verbose  mostra a saida de todos os passos

A ordem importa em dois pontos:
  - o a11y.py do Button mede tokens, entao roda antes do site; os outros a11y.py
    medem o HTML que o site emite, entao rodam depois dele;
  - o site roda duas vezes: a segunda le os a11y.json atualizados pela primeira
    passada dos portoes. As duas geracoes convergem; nao ha loop.

So usa a biblioteca padrao do Python (3.9 ou mais novo).
"""
import os, subprocess, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))

# Ordem de criacao dos componentes. Componente novo entra no fim.
COMPONENTS = [
    'button', 'icon', 'icon-button', 'tag', 'avatar', 'select', 'checkbox',
    'radio', 'switch', 'input', 'textarea', 'password', 'divider', 'card',
    'tab', 'accordion', 'modal', 'drawer', 'sidebar', 'breadcrumb', 'tooltip',
    'toast', 'alert',
]

# Passos extras que rodam antes do site, logo depois do check.py do componente.
BEFORE_SITE = {
    'button': ['a11y.py'],   # mede tokens, nao HTML
    'icon':   ['icons.py'],  # portao do desenho + manifesto
}

# O que o build escreve. O --check so olha estes caminhos, para nao reprovar
# por arquivo local que nao tem nada a ver com o build.
OUTPUTS = ['tokens.json', 'package.json', 'foundation', 'components', 'site']


def steps():
    out = [('foundation', 'export.py'), ('foundation', 'css.py')]
    for c in COMPONENTS:
        d = f'components/{c}'
        out += [(d, 'tokens.py'), (d, 'check.py')]
        out += [(d, s) for s in BEFORE_SITE.get(c, [])]
    out.append(('site', 'site.py'))
    for c in COMPONENTS:
        if 'a11y.py' not in BEFORE_SITE.get(c, []):
            out.append((f'components/{c}', 'a11y.py'))
    out.append(('site', 'site.py'))
    return out


def run(verbose):
    all_steps = steps()
    start = time.time()
    for i, (d, script) in enumerate(all_steps, 1):
        path = f'{d}/{script}'
        r = subprocess.run([sys.executable, path], cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           universal_newlines=True)
        status = 'ok' if r.returncode == 0 else f'FALHOU (saida {r.returncode})'
        print(f'[{i:2}/{len(all_steps)}] {path:34} {status}')
        if verbose or r.returncode != 0:
            print(r.stdout.rstrip())
        if r.returncode != 0:
            print(f'\nBuild parado no passo {i}: {path}')
            return False
    print(f'\n{len(all_steps)} passos, 0 falhas, {time.time() - start:.1f}s')
    return True


def check():
    r = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=all',
                        '--', *OUTPUTS], cwd=ROOT,
                       stdout=subprocess.PIPE, universal_newlines=True)
    changed = r.stdout.rstrip()
    if r.returncode != 0:
        print('Nao consegui rodar o git status.')
        return False
    if changed:
        print('\nO build gerou arquivos diferentes dos commitados:')
        print(changed)
        print('\nRode python3 build.py e commite os arquivos gerados junto com a mudanca.')
        return False
    print('Arquivos gerados iguais aos commitados.')
    return True


if __name__ == '__main__':
    args = sys.argv[1:]
    unknown = [a for a in args if a not in ('--check', '--verbose')]
    if unknown:
        sys.exit(f'Opcao desconhecida: {" ".join(unknown)}\n{__doc__}')
    ok = run('--verbose' in args)
    if ok and '--check' in args:
        ok = check()
    sys.exit(0 if ok else 1)
