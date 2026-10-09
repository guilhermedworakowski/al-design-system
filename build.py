"""
Build completo do AL Design System, num comando so.

Roda, na ordem certa, todos os geradores e portoes: Foundation, tokens e CSS de
cada componente, o site e o QA de acessibilidade de cada componente. Por
ultimo, monta o pacote em dist/ - so chega la se todos os portoes passaram.
Para no primeiro passo que falhar, e mostra a saida dele.

Rodar (da raiz do repo):
    python3 build.py            build completo
    python3 build.py --check    build completo e depois confere que o build nao
                                mexeu em nada fora de build/ e dist/ (e o que
                                o GitHub Actions roda em cada PR)
    python3 build.py --verbose  mostra a saida de todos os passos

A ordem importa em dois pontos:
  - o a11y.py do Button mede tokens, entao roda antes do site; os outros a11y.py
    medem o HTML que o site emite, entao rodam depois dele;
  - o site roda duas vezes: a segunda le os a11y.json atualizados pela primeira
    passada dos portoes. As duas geracoes convergem; nao ha loop;
  - num clone limpo ainda nao existe a11y.json, e o site nao monta sem eles.
    Entao, so nesse caso, cada a11y.py roda uma vez antes do site (o preparo):
    sem o HTML ele reprova o contrato de marcacao, mas grava os contrastes, e
    e isso que o site precisa. A falha do preparo e esperada e nao para o build;
    a passada que vale e a de depois do site.

Onde fica cada coisa (ver tools/paths.py): o que se escreve a mao mora em src/;
o que o build gera vai para build/ e dist/, que ficam fora do git.

So usa a biblioteca padrao do Python (3.9 ou mais novo).
"""
import os, subprocess, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from paths import COMPONENTS  # noqa: E402  - a lista mora em tools/paths.py

# Passos extras que rodam antes do site, logo depois do check.py do componente.
BEFORE_SITE = {
    'button': ['a11y.py'],   # mede tokens, nao HTML
    'icon':   ['icons.py'],  # portao do desenho + manifesto
}

# Tudo que o build gera vai para build/ e dist/, fora do git. O --check confere
# que, fora dessas pastas, o build nao mudou nem criou nenhum arquivo: um
# arquivo gerado que vazasse para o repo seria commitado sem ninguem perceber.


def steps():
    """Lista de (pasta, script, preparo). Passo de preparo pode falhar."""
    out = [('tools', 'guidegate.py', False),
           ('src/foundation', 'export.py', False), ('src/foundation', 'css.py', False)]
    for c in COMPONENTS:
        d = f'src/components/{c}'
        out += [(d, 'tokens.py', False), (d, 'check.py', False)]
        out += [(d, s, False) for s in BEFORE_SITE.get(c, [])]
    depois = [c for c in COMPONENTS if 'a11y.py' not in BEFORE_SITE.get(c, [])]
    for c in depois:
        if not os.path.exists(os.path.join(ROOT, 'build', 'components', c, 'a11y.json')):
            out.append((f'src/components/{c}', 'a11y.py', True))
    out.append(('site', 'site.py', False))
    for c in depois:
        out.append((f'src/components/{c}', 'a11y.py', False))
    out.append(('site', 'site.py', False))
    out.append(('tools', 'dist.py', False))
    return out


def run(verbose):
    all_steps = steps()
    start = time.time()
    for i, (d, script, preparo) in enumerate(all_steps, 1):
        path = f'{d}/{script}'
        r = subprocess.run([sys.executable, path], cwd=ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           universal_newlines=True)
        if r.returncode == 0:
            status = 'ok'
        elif preparo:
            status = 'preparo (sem o site ainda)'
        else:
            status = f'FALHOU (saida {r.returncode})'
        print(f'[{i:2}/{len(all_steps)}] {path:38} {status}')
        if verbose or (r.returncode != 0 and not preparo):
            print(r.stdout.rstrip())
        if r.returncode != 0 and not preparo:
            print(f'\nBuild parado no passo {i}: {path}')
            return False
    print(f'\n{len(all_steps)} passos, 0 falhas, {time.time() - start:.1f}s')
    return True


def check():
    r = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=all'],
                       cwd=ROOT,
                       stdout=subprocess.PIPE, universal_newlines=True)
    changed = r.stdout.rstrip()
    if r.returncode != 0:
        print('Nao consegui rodar o git status.')
        return False
    if changed:
        print('\nO repo mudou depois do build (fora de build/ e dist/):')
        print(changed)
        print('\nOu o build escreveu fora de build/ e dist/, ou havia mudanca nao'
              '\ncommitada antes de rodar. O --check precisa de um repo limpo.')
        return False
    print('Nada mudou no repo fora de build/ e dist/.')
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
