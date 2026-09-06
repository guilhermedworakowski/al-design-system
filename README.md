# AL Design System

Design system open source, do Figma ao código. Construído em público, uma camada de cada vez.

- **Licença:** MIT
- **Versão:** `0.2.0`
- **Figma:** biblioteca privada por enquanto — primitivas, semânticos e tokens de componente documentados abaixo

## Estado atual

A **Foundation** está fechada: primitivas de cor, camada semântica (dois temas), tipografia, espaçamento, radius, elevação e anel de foco — tudo gerado por código, nada digitado à mão no Figma ou na página de referência.

O **Button** é o primeiro componente a fechar as oito etapas do pipeline: auditado, tokenizado, documentado, codado, com playground e QA de acessibilidade.

| | |
|---|---|
| Primitivas de cor | 66 (6 famílias × 11 degraus) |
| Tokens semânticos | 49 × 2 temas |
| Pares de contraste validados | 80 — 77 em AA pleno, 3 exceções de marca nomeadas, 0 abaixo do piso |
| Componentes prontos | 1 (Button) |
| Tokens do Button | 46 — 38 alias, 8 transparentes, 0 valores soltos |

O plano de evolução completo — divisão de trabalho, pipeline por componente e roadmap em tiers — está no [playbook](https://claude.ai/code/artifact/18a0c1ed-949c-4c8d-8906-93c21ed560a3).

## Estrutura

```
foundation/
  color.py       # motor OKLCH -> sRGB, gamut mapping, contraste
  build.py       # camada semântica + portão de contraste (WCAG 2.1 AA)
  export.py      # gera tokens.json a partir de color.py + build.py
  css.py         # gera al-foundation.css a partir de tokens.json
  tune.py        # scripts de calibração da rampa neutra

components/button/
  tokens.py      # camada de alias do Button + portão de alias, gera tokens.json e o CSS
  button.css     # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal em button.css
  a11y.py        # QA de acessibilidade por combinação renderizada

site/
  site.py        # gera index.html: o site — Foundation + componentes, navegação e playground
```

Arquivos `tokens.json`, `*.css` gerados e `site/index.html` são saída — versionados para consulta, mas nunca editados à mão.

Todo script resolve caminho a partir de si mesmo, nunca do diretório de onde é chamado: rodar da raiz ou de dentro da própria pasta dá exatamente o mesmo resultado. Existe **um** `tokens.json`, na raiz, e ele é a fonte da verdade de toda a cadeia.

O `site/index.html` é o site: ele lê o `tokens.json` e embute o `al-foundation.css`, os tokens do Button e o `button.css` reais, então nenhuma contagem e nenhum componente ali é uma cópia — se um componente quebrar, a página quebra junto.

> As páginas avulsas que existiram antes (`foundation/page.py` → `foundation.html` e `site/build.py` → `site/button.html`) foram removidas quando o site as absorveu. Elas continuam recuperáveis na tag `v0.2.0`, mas os números da prosa daquelas páginas estavam desatualizados — não use como referência.

## Rodando localmente

```bash
python3 foundation/export.py       # tokens.json + portão de contraste
python3 foundation/css.py          # al-foundation.css
python3 components/button/tokens.py  # tokens do Button + portão de alias + CSS
python3 components/button/check.py   # portão do CSS do componente
python3 components/button/a11y.py    # QA de acessibilidade
python3 site/site.py               # o site: Foundation + componentes
```

Nesta ordem, e de qualquer diretório.

## Os portões

Validação é parte do build, não checagem opcional. Cada camada tem o seu, e cada um aborta com saída diferente de zero:

| Portão | Onde | O que recusa |
|---|---|---|
| Contraste | `foundation/export.py` | Qualquer par de cor abaixo do mínimo WCAG. Exceções de marca são nomeadas uma a uma e nunca descem de 3:1. |
| Alias | `components/button/tokens.py` | Token de componente com valor próprio — hex, px, ou nome semântico inexistente. |
| CSS literal | `components/button/check.py` | Cor, comprimento ou peso literal dentro de `button.css`. |
| Acessibilidade | `components/button/a11y.py` | Combinação renderizada (variante × estado × tema) fora do mínimo, medida contra o fundo efetivo. |

## Arquitetura de tokens

Três camadas, cada uma com um trabalho:

1. **Primitiva** — escala de cor em OKLCH, uma única escada de lightness compartilhada por todas as famílias, ancorada na cor de marca. Nenhum componente consome esta camada direto.
2. **Semântica** — papel de uso (`bg-brand`, `text-secondary`, `border-focus`), com um valor por tema. É onde o tema é resolvido.
3. **Componente** — alias do semântico, um por papel do componente (`button-primary-bg-hover`). Só diverge para uma primitiva quando o componente exige. Nunca hex solto.

Em CSS, a camada de componente não tem bloco de tema — e não precisa. O tema troca no `:root`, que é o mesmo elemento onde os alias são declarados, então o `:root` re-substitui todos de uma vez.

> Substituição de custom property acontece no elemento onde ela é **declarada**, não no ponto de uso. Um alias declarado no `:root` desce já resolvido. Tematizar um container solto — e não o `:root` — exige re-declarar a camada dentro dele; é o que `site/site.py` faz para o playground.

**Nomenclatura:** o nome do token separa níveis com hífen (`bg-brand`, `button-primary-bg-hover`). No Figma, a mesma coisa vive em pasta dentro da collection do componente (`primary/bg-hover` na collection `4. Button`) — a barra é o mecanismo de agrupamento do painel de variáveis, não parte do nome do token.

## Pendências registradas

Coisas deliberadamente não construídas, anotadas para não voltarem como dúvida:

- **Escala de ícone** — o Button usa 16px e o `Icon Button` usa 20px, mas a escala pertence ao componente `Icon`, do Tier 1. Fica em `pending` no `tokens.json` do Button.
- **Escala de motion** — as durações no `button.css` são literais e aparecem no relatório do `check.py` como exceção consciente.
- **Unidade de tipografia** — a escala é em `px`. Atende o critério 1.4.4 (zoom do navegador escala `px`), mas não acompanha a preferência de tamanho de fonte do usuário. Migrar para `rem` é decisão de Foundation, não de componente.

## Contribuindo

Projeto em estágio inicial, mantido por [@guilhermedworakowski](https://github.com/guilhermedworakowski). Guia de contribuição chega quando o projeto tiver colaboradores externos ativos.

## Licença

[MIT](LICENSE) © 2026 Guilherme Domingues
