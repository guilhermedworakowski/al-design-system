from color import *
from build import SEM, PAIRS, EXCEPTIONS, HARD_FLOOR
import json, os

# Caminho ancorado no proprio arquivo, nunca no diretorio de onde se roda:
# tokens.json e a fonte unica da verdade e mora na raiz. Antes daqui o destino
# dependia do cwd, e rodar de dentro de foundation/ criava uma segunda copia
# que os portoes liam sem ninguem perceber.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_PATH = os.path.join(ROOT, 'tokens.json')

P = build()
SHADOW_RGB = "24, 24, 24"   # neutral-950 acromatico -> sombra cinza, sem tingimento de hue

TOKENS = {
  "meta": {
    # Terceira casa = release. Atualizacao numa fundacao ou num componente que
    # ja existe entra aqui; casa do meio fica para camada nova. 0.3.1: o Button
    # subiu o icone para a entrelinha do rotulo (0.1.1 -> 0.2.0).
    # 0.4.0: o Icon Button entrou inteiro - componente novo e camada nova, entao
    # casa do meio. Trouxe collection propria no Figma, 42 tokens, CSS, dois
    # portoes e pagina no site.
    # 0.5.0: o Tag - primeiro componente do AL a fechar em zero excecoes
    # carregando texto (piso 4.5:1, nao os 3:1 do Icon Button).
    # 0.6.0: o Avatar - componente novo, casa do meio. Fecha o Tier 1. Nao
    # cria par de contraste novo (zero excecoes), e o menor portao de a11y do
    # sistema ate agora: o fundo nunca varia por tipo, so por tema.
    # 0.10.0: o Switch - componente novo, casa do meio. Primeiro componente a
    # criar semantico na Foundation (bg-thumb, bg-thumb-disabled), e o primeiro
    # que o proprio site consome: o switch de tema do trilho.
    # 0.11.0: o Input - componente novo, casa do meio. Primeiro com read-only
    # (que NAO e isento de contraste como o disabled) e com afixos dentro da
    # borda: a caixa e um invólucro, e o estado chega a ela por :has().
    # 0.11.1: package.json — distribuição; nenhum token muda
    # 0.13.0: o Password - componente novo, casa do meio. Primeiro componente
    # com JavaScript proprio (password.js), que passa a ir no pacote.
    # 0.14.0: o Divider - componente novo, casa do meio. Primeiro do Tier 3
    # (estrutura); nenhum token da Foundation muda.
    # 0.15.0: o Card - componente novo, casa do meio. Segundo do Tier 3;
    # nenhum token da Foundation muda.
    # 0.16.0: o Tab - componente novo, casa do meio. Terceiro do Tier 3 e o
    # primeiro com script proprio (tab.js); nenhum token da Foundation muda.
    # 0.17.0: o Accordion - componente novo, casa do meio. Quarto do Tier 3,
    # <details>/<summary> nativo, sem script. A Foundation ganha dois
    # semanticos, bg-hover-raised e bg-active-raised: no escuro o bg-hover era
    # a mesma cor da superficie elevada e o hover sumia.
    # 0.17.1: Motion - atualizacao da Foundation, terceira casa. Quatro tokens
    # (duration-panel/popup, easing-enter/exit) para o que entra e sai da tela;
    # nenhum componente consome ainda, e os 120ms literais seguem pendentes.
    "name": "AL Design System", "version": "0.17.1", "license": "MIT",
    "brandAnchor": "#FC5000", "colorSpace": "OKLCH", "wcag": "2.1 AA",
    "lLadder": L_LADDER, "neutralHue": NEUTRAL_HUE,
  },
  "color": {"primitive": P, "semantic": SEM, "brandHover": BRAND_HOVER},
  "type": {
    "family": {
      "sans": "'InterVariable', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      "mono": "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace",
    },
    "weight": {"regular": 400, "medium": 500, "semibold": 600, "bold": 700},
    "size":  {"xs":12,"sm":14,"md":16,"lg":18,"xl":20,"2xl":24,"3xl":30,"4xl":36,"5xl":48,"6xl":60},
    "leading": {"xs":16,"sm":20,"md":24,"lg":28,"xl":28,"2xl":32,"3xl":36,"4xl":44,"5xl":56,"6xl":68},
    "tracking": {"xs":"0.01em","sm":"0em","md":"0em","lg":"0em","xl":"-0.01em","2xl":"-0.01em",
                 "3xl":"-0.015em","4xl":"-0.02em","5xl":"-0.02em","6xl":"-0.025em"},
    "styles": [
      # nome,          size, leading, weight, tracking,   uso
      ("display-2xl",   60, 68, 700, "-0.025em", "hero / numero de destaque"),
      ("display-xl",    48, 56, 700, "-0.02em",  "titulo de pagina de marketing"),
      ("heading-lg",    36, 44, 600, "-0.02em",  "H1 de produto"),
      ("heading-md",    30, 36, 600, "-0.015em", "H2"),
      ("heading-sm",    24, 32, 600, "-0.01em",  "H3 / titulo de card"),
      ("heading-xs",    20, 28, 600, "-0.01em",  "H4 / titulo de secao"),
      ("body-lg",       18, 28, 400, "0em",      "lead / intro"),
      ("body-md",       16, 24, 400, "0em",      "corpo padrao do sistema"),
      ("body-sm",       14, 20, 400, "0em",      "texto de apoio / tabela"),
      ("label-lg",      16, 24, 500, "0em",      "label de botao grande"),
      ("label-md",      14, 20, 500, "0em",      "label de campo / botao"),
      ("label-sm",      12, 16, 500, "0.01em",   "badge / tag / overline"),
      ("caption",       12, 16, 400, "0.01em",   "legenda / helper text"),
      ("code-md",       14, 20, 400, "0em",      "codigo inline e bloco"),
    ],
  },
  "space": {str(v): v for v in [0,2,4,8,12,16,20,24,32,40,48,64,80,96]},
  "radius": {"none":0,"xs":2,"sm":4,"md":6,"lg":8,"xl":12,"2xl":16,"3xl":24,"full":9999},
  # Escala de tamanho de icone. Os degraus sao nomeados pelo proprio valor,
  # como o espacamento - e de proposito: nome de camiseta (sm/md/lg) obriga a
  # renomear quando um degrau entra no meio, e esta e a escala que mais cresce.
  # Assim um degrau novo custa uma linha e nada existente muda de nome.
  #
  # A escala NAO prende o componente Icon. O desenho e de 24 com o traco
  # vetorizado em preenchimento, entao a instancia vale em qualquer tamanho.
  # Isto aqui nomeia os tamanhos recorrentes para que a decisao seja tomada
  # uma vez e mudavel num lugar so - e para que o portao de CSS literal tenha
  # contra o que validar.
  "iconSize": {"16":16, "20":20, "24":24, "32":32},
  "border": {"width": {"0":0,"1":1,"2":2,"focus":2}, "focusOffset": 2},
  # Motion. Dois eixos, e o segundo e escolha de quem consome:
  #   easing   -> o TIPO DA ACAO (entrada ou saida). Entrada desacelera
  #               (ease-out): o elemento chega e assenta. Saida acelera
  #               (ease-in): o elemento parte e some.
  #   duration -> o PORTE de quem se move, nao o nome do componente. Nome de
  #               componente obrigaria um token novo a cada componente novo;
  #               porte nao. `panel` cobre o que ocupa a tela (Modal, Drawer),
  #               `popup` o que aparece pequeno por cima dela (Tooltip, Toast).
  # Entrada e saida tem a mesma duracao por decisao de Gui (08/10/2026); se
  # um dia divergirem, o token novo e `duration-panel-exit`, sem renomear.
  # As curvas sao as palavras-chave do CSS escritas por extenso: o Figma, o
  # JS e o grafico do site precisam dos quatro numeros, nao do apelido.
  "motion": {
    "duration": {"panel": 300, "popup": 200},
    "easing": {"enter": [0, 0, 0.58, 1], "exit": [0.42, 0, 1, 1]},
    "uso": {
      "duration-panel": "Modal e Drawer: o que cobre a tela ou entra por uma borda dela. Entrada e saida.",
      "duration-popup": "Tooltip e Toast: o que aparece pequeno por cima da tela. Entrada e saida.",
      "easing-enter": "Tudo que entra (ease-out): chega rapido e assenta devagar.",
      "easing-exit": "Tudo que sai (ease-in): parte devagar e acelera ate sumir.",
    },
    "_note": "Sob prefers-reduced-motion o componente zera a transicao (transition: none). "
             "Nao existe token de duracao zero: ausencia de movimento nao e um valor de escala.",
  },
  "focusRing": {
    # Duas camadas na mesma sombra, sem offset:
    #   interna  -> spread 2, na cor do fundo. E o respiro. Impede o anel de
    #               encostar no preenchimento do componente.
    #   externa  -> spread 4 (2 do respiro + 2 do anel), na cor do foco.
    # Assim o anel so precisa contrastar com o fundo da tela - e o preenchimento
    # do botao, seja laranja ou vermelho, deixa de ser um problema.
    "default": {
      "light": f"0 0 0 2px {SEM['bg-canvas'][0]}, 0 0 0 4px {SEM['shadow-focus-default'][0]}",
      "dark":  f"0 0 0 2px {SEM['bg-canvas'][1]}, 0 0 0 4px {SEM['shadow-focus-default'][1]}",
    },
    "error": {
      "light": f"0 0 0 2px {SEM['bg-canvas'][0]}, 0 0 0 4px {SEM['shadow-focus-error'][0]}",
      "dark":  f"0 0 0 2px {SEM['bg-canvas'][1]}, 0 0 0 4px {SEM['shadow-focus-error'][1]}",
    },
    "_note": "Nao e elevacao. Elevacao comunica altura; isto comunica foco de teclado "
             "e passa pelo portao de contraste. Nunca some, nunca anima.",
  },
  "elevation": {
    "0":  {"light":"none", "dark":"none"},
    "1":  {"light":f"0 1px 2px 0 rgba({SHADOW_RGB},0.06), 0 1px 3px 0 rgba({SHADOW_RGB},0.10)",
           "dark": f"0 1px 2px 0 rgba(0,0,0,0.30), 0 1px 3px 0 rgba(0,0,0,0.40)"},
    "2":  {"light":f"0 2px 4px -1px rgba({SHADOW_RGB},0.06), 0 4px 8px -2px rgba({SHADOW_RGB},0.10)",
           "dark": f"0 2px 4px -1px rgba(0,0,0,0.32), 0 4px 8px -2px rgba(0,0,0,0.44)"},
    "3":  {"light":f"0 4px 8px -2px rgba({SHADOW_RGB},0.06), 0 8px 16px -4px rgba({SHADOW_RGB},0.12)",
           "dark": f"0 4px 8px -2px rgba(0,0,0,0.34), 0 8px 16px -4px rgba(0,0,0,0.48)"},
    "4":  {"light":f"0 8px 16px -4px rgba({SHADOW_RGB},0.08), 0 16px 32px -8px rgba({SHADOW_RGB},0.14)",
           "dark": f"0 8px 16px -4px rgba(0,0,0,0.36), 0 16px 32px -8px rgba(0,0,0,0.52)"},
    "5":  {"light":f"0 16px 32px -8px rgba({SHADOW_RGB},0.10), 0 32px 64px -16px rgba({SHADOW_RGB},0.18)",
           "dark": f"0 16px 32px -8px rgba(0,0,0,0.40), 0 32px 64px -16px rgba(0,0,0,0.56)"},
    "_note": "No escuro a sombra e cue secundario: o cue primario e a superficie clarear (950 -> 900 -> 800).",
  },
}

# relatorio de contraste embutido (o portao vira dado, nao so log)
report = []
for i, theme in enumerate(('light','dark')):
    for fg, bg, mn, label in PAIRS:
        a, b = SEM[fg][i], SEM[bg][i]
        exc = (theme, fg, bg) in EXCEPTIONS
        floor = HARD_FLOOR if exc else mn
        report.append({"theme":theme,"label":label,"fg":fg,"bg":bg,
                       "fgHex":a,"bgHex":b,"ratio":round(cr(a,b),2),"min":floor,
                       "pass":cr(a,b)>=floor,"exception":exc})

fails = [r for r in report if not r["pass"]]
if fails:
    raise SystemExit(f"{len(fails)} par(es) reprovam o gate de contraste — export abortado: {fails}")

TOKENS["contrastReport"] = report

json.dump(TOKENS, open(TOKENS_PATH,'w'), indent=2, ensure_ascii=False)

# A versao tem uma fonte so: meta.version, acima. O package.json repete o
# numero para o npm, e quem o regrava e este script - nunca a mao. Fica depois
# do portao de contraste: export abortado nao sobe versao de pacote.
PACKAGE_PATH = os.path.join(ROOT, 'package.json')
pkg = json.load(open(PACKAGE_PATH, encoding='utf-8'))
pkg['version'] = TOKENS['meta']['version']
with open(PACKAGE_PATH, 'w', encoding='utf-8') as f:
    json.dump(pkg, f, indent=2, ensure_ascii=False)
    f.write('\n')
n_prim = sum(len(v) for v in P.values()) + 1
print(f"tokens.json escrito")
print(f"package.json na versao {pkg['version']}")
print(f"  primitivas de cor : {n_prim}  ({len(P)} familias x 11 steps + orange-550)")
print(f"  semanticos de cor : {len(SEM)} x 2 temas = {len(SEM)*2}")
print(f"  estilos de texto  : {len(TOKENS['type']['styles'])}")
print(f"  espacamento       : {len(TOKENS['space'])}   radius: {len(TOKENS['radius'])}   icon-size: {len(TOKENS['iconSize'])}   elevacao: 6")
n_exc = sum(1 for r in report if r['exception'])
print(f"  pares validados   : {len(report)}  |  AA pleno: {len(report)-n_exc}  |  excecoes de marca: {n_exc}  |  reprovas: {sum(1 for r in report if not r['pass'])}")
TOKENS['meta']['brandLabel'] = 'light'
TOKENS['meta']['exceptions'] = [{'theme':r['theme'],'label':r['label'],'ratio':r['ratio']} for r in report if r['exception']]
total = n_prim + len(SEM)*2 + len(TOKENS['type']['styles']) + len(TOKENS['space']) + len(TOKENS['radius']) + len(TOKENS['iconSize']) + 6 + 4
print(f"  TOTAL             : ~{total} tokens")
