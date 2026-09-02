# AL Design System

Design system open source, do Figma ao código. Construído em público, uma camada de cada vez.

- **Licença:** MIT
- **Versão:** `0.1.0`
- **Figma:** biblioteca privada por enquanto — os primitivos, semânticos e o roadmap completo estão documentados abaixo

## Estado atual

A **Foundation** está fechada: primitivos de cor, camada semântica (dois temas), tipografia, espaçamento, radius e elevação — tudo gerado por código, nada digitado à mão no Figma ou na página de referência.

Nenhum componente está tokenizado, documentado ou codado ainda. Os component sets do `Button` existem no Figma como ponto de partida para um redesenho manual — não são o Button final do sistema.

| | |
|---|---|
| Primitivas de cor | 66 (6 famílias × 11 degraus) |
| Tokens semânticos | 47 × 2 temas |
| Pares de contraste validados | 72 — 69 em AA pleno, 3 exceções de marca nomeadas, 0 abaixo do piso |
| Componentes prontos | 0 |

O plano de evolução completo — divisão de trabalho, pipeline por componente e roadmap em tiers — está no [playbook](https://claude.ai/code/artifact/18a0c1ed-949c-4c8d-8906-93c21ed560a3).

## Estrutura

```
foundation/
  color.py       # motor OKLCH -> sRGB, gamut mapping, contraste
  build.py       # camada semântica + portão de contraste (WCAG 2.1 AA)
  export.py      # gera tokens.json a partir de color.py + build.py
  page.py        # gera foundation.html a partir de tokens.json
  tune.py        # scripts de calibração da rampa neutra
  tokens.json    # token set exportado (gerado, não editar à mão)
  foundation.html
```

## Rodando localmente

```bash
cd foundation
python3 export.py   # regenera tokens.json e roda o portão de contraste
python3 page.py      # regenera foundation.html a partir de tokens.json
```

`export.py` aborta com erro se qualquer par de contraste reprovar — o portão é parte do build, não uma checagem opcional.

## Arquitetura de tokens

Duas camadas hoje, uma terceira reservada para quando um componente precisar divergir do semântico:

1. **Primitiva** — escala de cor em OKLCH, uma única escada de lightness compartilhada por todas as famílias, ancorada na cor de marca.
2. **Semântica** — papel de uso (`bg-brand`, `text-secondary`, `border-focus`), com um valor por tema. É esta camada que todo componente deveria consumir por padrão.
3. **Componente** — só existe quando um valor precisa divergir do semântico para aquele componente específico. Nenhum token de componente existe hoje; entra junto com o primeiro componente construído do zero.

**Nomenclatura:** o nome do token separa níveis com hífen (`bg-brand`, `button-primary-bg-hover`). No Figma, a mesma coisa vive em pasta (`bg/brand`, `button/primary/bg/hover`) — a barra é o mecanismo de agrupamento do painel de variáveis, não parte do nome do token.

## Contribuindo

Projeto em estágio inicial, mantido por [@guilhermedworakowski](https://github.com/guilhermedworakowski). Guia de contribuição chega quando o projeto tiver colaboradores externos ativos.

## Licença

[MIT](LICENSE) © 2026 Guilherme Domingues
