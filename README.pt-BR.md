# AL Design System

[![npm](https://img.shields.io/npm/v/al-design-system)](https://www.npmjs.com/package/al-design-system)
[![licença](https://img.shields.io/github/license/guilhermedworakowski/al-design-system)](LICENSE)
[![build](https://github.com/guilhermedworakowski/al-design-system/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/guilhermedworakowski/al-design-system/actions/workflows/build.yml)

Design system open source, do Figma ao código. CSS puro, um pouco de JavaScript sem framework só onde o CSS não alcança, e nenhuma dependência.

[English](README.md) · **Português** · [Site de documentação](https://al.guilhermedesignd.com)

## O que é

- **Foundation + 23 componentes**, desenhados no Figma e codados a partir dos mesmos tokens.
- **Temas claro e escuro** já incluídos. Por padrão segue o sistema operacional, e dá para forçar um.
- **A acessibilidade é conferida no build.** Cada combinação renderizada (variante × estado × tema) tem o contraste medido contra o fundo onde ela realmente aparece, e o contrato de marcação de cada componente é verificado. Se algo reprova, o build para.
- **Nada é digitado à mão.** Tokens, variáveis CSS, `tokens.json` e as tabelas da documentação saem todos de uma fonte só.

## Componentes

| Grupo | Componente | Script | Diretrizes |
|---|---|:---:|---|
| Ações e exibição | Button | | [diretrizes](src/components/button/guidelines.md) |
| | Icon | | (70 ícones, ver [Ícones](#ícones)) |
| | Icon Button | | [diretrizes](src/components/icon-button/guidelines.md) |
| | Tag | | [diretrizes](src/components/tag/guidelines.md) |
| | Avatar | | [diretrizes](src/components/avatar/guidelines.md) |
| Formulários | Select | | [diretrizes](src/components/select/guidelines.md) |
| | Checkbox | | [diretrizes](src/components/checkbox/guidelines.md) |
| | Radio | | [diretrizes](src/components/radio/guidelines.md) |
| | Switch | | [diretrizes](src/components/switch/guidelines.md) |
| | Input | | [diretrizes](src/components/input/guidelines.md) |
| | Textarea | | [diretrizes](src/components/textarea/guidelines.md) |
| | Password | ✓ | [diretrizes](src/components/password/guidelines.md) |
| Estrutura e sobreposição | Divider | | [diretrizes](src/components/divider/guidelines.md) |
| | Card | | [diretrizes](src/components/card/guidelines.md) |
| | Tab | ✓ | [diretrizes](src/components/tab/guidelines.md) |
| | Accordion | | [diretrizes](src/components/accordion/guidelines.md) |
| | Modal | ✓ | [diretrizes](src/components/modal/guidelines.md) |
| | Drawer | ✓ | [diretrizes](src/components/drawer/guidelines.md) |
| Navegação | Sidebar | ✓ | [diretrizes](src/components/sidebar/guidelines.md) |
| | Breadcrumb | ✓ | [diretrizes](src/components/breadcrumb/guidelines.md) |
| Feedback | Tooltip | ✓ | [diretrizes](src/components/tooltip/guidelines.md) |
| | Toast | ✓ | [diretrizes](src/components/toast/guidelines.md) |
| | Alert | ✓ | [diretrizes](src/components/alert/guidelines.md) |

Cada arquivo de diretrizes traz as regras de uso (quando usar, quando não usar, conteúdo, comportamento e acessibilidade) e, quando houver, as exceções de contraste que o componente declara. Por enquanto as diretrizes estão em inglês; a versão em português chega junto com o site novo.

## Instalação

```bash
npm install al-design-system
```

Ou direto de uma CDN, fixado numa versão:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/al-design-system@1.0.1/dist/al.css">
```

Cada [Release no GitHub](https://github.com/guilhermedworakowski/al-design-system/releases) também traz a pasta `dist/` num zip.

### O que vem no pacote

| Arquivo | O que é |
|---|---|
| `al.css` | Foundation + os 23 componentes, num arquivo só |
| `foundation.css` | Só a Foundation: cor, tipografia, espaçamento, radius, tamanho de ícone, elevação, anel de foco e motion |
| `components/<nome>.css` | Um componente (os tokens + o CSS dele) |
| `components/<nome>.js` | O comportamento, para os 9 componentes que têm script |
| `icons/*.svg`, `icons/icons.json` | Os 70 ícones |
| `tokens.json` | Os tokens da Foundation, para ler por código |

## Uso

### CSS

O jeito mais simples é tudo de uma vez:

```js
import 'al-design-system';            // o mesmo que al-design-system/al.css
```

Ou só o que o produto usa. A Foundation vem sempre primeiro, porque todo token de componente aponta para um token dela:

```js
import 'al-design-system/foundation.css';
import 'al-design-system/components/button.css';
```

Depois, a marcação usa as classes `.al-*`:

```html
<button type="button" class="al-btn al-btn--primary al-btn--md">Salvar</button>
```

A marcação exata de cada componente (qual elemento, quais atributos) está descrita no topo do CSS dele e no [site de documentação](https://al.guilhermedesignd.com).

### Scripts

Password, Tab, Modal, Drawer, Sidebar, Breadcrumb, Tooltip, Toast e Alert precisam do script, carregado uma vez por página. Cada um liga sozinho os componentes que já estão na página:

```html
<script src="node_modules/al-design-system/dist/components/modal.js" defer></script>
```

Conteúdo inserido depois é ligado com `init`, por exemplo `window.alModals.init(elemento)`. Toast e Alert são abertos por código: `alToast.show(...)` e `alAlert.show(...)`. O uso de cada script está no topo do arquivo.

### Tema

Sem nada no `<html>`, o tema segue o sistema operacional (`prefers-color-scheme`). Para forçar um:

```html
<html data-theme="dark">
```

### Fontes

As fontes não vêm no pacote. A Foundation pede `Inter` e `JetBrains Mono`, com fontes do sistema como reserva. Carregar os arquivos de fonte fica com o produto, de preferência hospedados junto com ele.

### Ícones

Os SVGs entram inline, com a classe `.al-icon` no próprio `<svg>`, para herdarem a cor do texto (o `<img>` não herda). O arquivo traz só o desenho. O contrato de acessibilidade é acrescentado por quem usa:

- decorativo: `aria-hidden="true" focusable="false"`;
- carrega sentido: `role="img"` e um `aria-label`.

## Tokens

Três camadas, cada uma com um trabalho:

1. **Primitiva**: as escalas de cor cruas, em OKLCH, numa única escada de lightness compartilhada por todas as famílias. Nenhum componente usa direto.
2. **Semântica**: o papel (`bg-brand`, `text-secondary`, `border-focus`), com um valor por tema. É onde o tema é resolvido.
3. **Componente**: um alias de um token semântico, um por papel do componente (`button-primary-bg-hover`). Nunca um hex solto.

No CSS, são custom properties com o prefixo `--al-`. O `tokens.json` tem os mesmos valores para quem quiser ler por código.

## Acessibilidade

Os mínimos são os de contraste do WCAG: 4,5:1 para texto, 3:1 para ícone, borda e foco. Quando a cor da marca não chega ao mínimo, a exceção é nomeada uma a uma, nunca desce de 3:1 e é paga com uma regra de uso (um rótulo visível, um título, uma segunda pista). Quando um componente tem exceções, elas estão listadas nas diretrizes dele.

Além do contraste, cada componente tem um contrato de marcação conferido contra o HTML: o elemento nativo certo, um nome acessível, os atributos certos, nada interativo onde não deve.

## Versionamento

O AL segue o versionamento semântico, lido assim:

- **terceira casa** (1.0.**1**): ajuste, sem componente ou camada nova;
- **casa do meio** (1.**1**.0): componente ou camada nova;
- **primeira casa** (**2**.0.0): mudança que quebra o que já existe.

O que mudou em cada versão está no [CHANGELOG](CHANGELOG.md).

## Estrutura do repositório

```
src/foundation/        a fonte da Foundation (cor, tipografia, espaçamento...) em Python
src/components/<nome>/ uma pasta por componente:
  tokens.py              os tokens do componente (alias da Foundation)
  <nome>.css             o CSS escrito à mão
  <nome>.js              o script, quando existe
  check.py, a11y.py      os portões (CSS literal, token órfão, contraste, marcação)
  guidelines.md          as regras de uso
site/                  o gerador do site de documentação
tools/                 o que o build compartilha (caminhos, montagem do dist)
build.py               roda tudo, na ordem
build/                 saída gerada (CSS, tokens, site)
dist/                  o pacote que vai para o npm
```

Para gerar a partir do código, basta o Python 3.9 ou mais novo, sem nenhum pacote para instalar:

```bash
python3 build.py
```

Ele regera tudo e roda todos os portões. Os detalhes estão no [CONTRIBUTING](CONTRIBUTING.md) (em inglês).

## Licença

[MIT](LICENSE) © 2026 Guilherme Domingues. Os ícones vêm do [Lucide](https://lucide.dev) (ISC); ver [`icons/NOTICE`](src/components/icon/NOTICE).
