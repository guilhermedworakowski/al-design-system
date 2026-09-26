# AL Design System

Design system open source, do Figma ao código. Construído em público, uma camada de cada vez.

- **Licença:** MIT
- **Versão:** `0.10.0`
- **Figma:** biblioteca privada por enquanto — primitivas, semânticos e tokens de componente documentados abaixo

## Estado atual

A **Foundation** está fechada: primitivas de cor, camada semântica (dois temas), tipografia, espaçamento, radius, tamanho de ícone, elevação e anel de foco — tudo gerado por código, nada digitado à mão no Figma ou na página de referência.

O **Button** é o primeiro componente a fechar as oito etapas do pipeline: auditado, tokenizado, documentado, codado, com playground e QA de acessibilidade.

O **Icon Button** é o segundo, e fechou as oito no mesmo formato. Ele é o Button sem rótulo visível — e essa ausência muda mais do que parece: o ícone passa a ser o único portador do sentido, o nome acessível vira contrato obrigatório em vez de recurso, e o piso de contraste desce de 4,5:1 para 3:1, porque o critério que vale é o 1.4.11 (não-textual) e não o 1.4.3. A consequência prática é que ele não tem nenhuma exceção de marca, enquanto o Button tem três — é a mesma cor medida contra um mínimo diferente.

O **Tag** é o terceiro, e é o primeiro do AL a fechar em **zero exceções de contraste carregando texto**. O Icon Button já fechava em zero, mas contra o piso de 3:1 do critério 1.4.11 — o portador do sentido dele é um ícone. Aqui o portador é um rótulo, então o piso é o 4,5:1 do 1.4.3, e a consequência mudou o escopo: o status Brand ficou de fora, porque branco sobre o laranja da marca dá 3,34:1 — o mesmo par que no Icon Button é aprovação. Ele também é o único componente sem nenhuma transição, e por isso o único sem pendência de escala de motion.

O **Icon** fechou sete das oito, pulando a documentação por decisão: ícone do AL vive dentro de acionável e quem carrega o sentido é o rótulo. O contrato de acessibilidade não foi pulado junto — ele virou portão, medido no HTML emitido, em vez de regra escrita.

O **Avatar** é o quarto, e fecha o Tier 1. Diferente dos outros três, os tipos dele não são uma escolha de variante — são uma cadeia: Photo se houver foto, Iniciais se houver nome, Icon como último recurso, nessa ordem, nunca uma caixa vazia. É também o menor portão de acessibilidade do sistema até agora: o fundo não varia por tipo nem por status, só por tema, então sobram quatro medições — e, como o Tag, fecha em zero exceções de contraste.

O **Select** abre o Tier 2 (formulário). É o `<select>` nativo: a lista aberta é desenhada pelo navegador, e o componente entrega o gatilho fechado — a distinção do Carbon entre *Select* e *Dropdown*/*ComboBox*. O que isso compra é teclado, leitor de tela e comportamento mobile sem uma linha de JavaScript. Ele marca o campo **opcional**, não o obrigatório, e traz duas exceções declaradas: a borda de repouso abaixo de 3:1, sustentada pela regra do rótulo visível, e o disabled abaixo de AA. Com ele entraram dois portões novos: token órfão (token declarado que o CSS nunca consome reprova) e o contrato de marcação de formulário.

O **Checkbox** é o segundo do Tier 2. É o `<input type="checkbox">` nativo com a caixa do AL pintada por cima, e o estado misto (indeterminado) só existe por JavaScript — não há atributo HTML. O Figma tem um eixo só de estado; as combinações que ele não desenha (marcado + foco, erro + marcado, marcado + desabilitado) são pintadas pelo código com os mesmos tokens. O componente não tem mensagem de erro de propósito: o formulário é obrigado a descrever o erro em texto, porque borda e rótulo vermelhos são só cor (WCAG 3.3.1 e 1.4.1). O portão dele mede contra três fundos — tela, faixa de seção e card — e mostra que, marcada, quem desenha a caixa é o preenchimento, não a borda.

O **Radio** é o terceiro do Tier 2. É o `<input type="radio">` nativo com o círculo do AL pintado por cima: setas, Tab entrando na pergunta uma vez só e "marcar um desmarca o outro" vêm do navegador. A diferença estrutural para o Checkbox é que o marcado **não pinta o fundo** — é borda laranja + ponto de 14px, com o anel branco entre os dois —, então saem `bg-checked` e o ícone, e entram `dot` e `dot-disabled`. Não existe componente de grupo, de propósito: a pergunta é `<fieldset>` + `<legend>` nativos, montados pela aplicação. E o **erro é da pergunta, não da opção**, como no Primer, no Carbon, no Spectrum e no Polaris: o `radio.css` lê `aria-invalid` no `fieldset`, nunca no radio, e marcar a pergunta uma vez acende todas as opções. Mesmas duas exceções declaradas do Checkbox.

O **Switch** é o quarto do Tier 2. É o `<input type="checkbox" role="switch">` nativo com o trilho do AL pintado por cima — o leitor de tela anuncia "chave, ligada", e Espaço alterna (Enter não, como no checkbox nativo). Ele liga ou desliga algo que **vale na hora**, sem botão "Salvar", e por isso não tem estado de erro: escolha que precisa ser validada é Checkbox (Spectrum, Polaris). Quando a ação falha, a bolinha volta ao estado real e a aplicação avisa em texto. Foi o primeiro componente a criar token na Foundation: `bg-thumb` e `bg-thumb-disabled`, semânticos com claro e escuro para a peça que desliza sobre um trilho. A bolinha desligada fica abaixo de 3:1 por decisão de design (`neutral-400` é o teto), sustentada pelo trilho laranja do ligado e pelo rótulo visível — três exceções declaradas no total. E é o primeiro componente que o próprio site consome: o switch de tema do trilho era um `<button role="switch">` feito à mão, o portão de marcação do Switch o reprovou, e ele passou a ser o componente.

Todo input do Tier 2 tem **um tamanho só**, por regra.

| | |
|---|---|
| Primitivas de cor | 66 (6 famílias × 11 degraus) |
| Tokens semânticos | 51 × 2 temas |
| Pares de contraste validados | 80 — 77 em AA pleno, 3 exceções de marca nomeadas, 0 abaixo do piso |
| Componentes prontos | 8 (Button, Icon Button, Tag, Avatar, Select, Checkbox, Radio, Switch) |
| Ícones | 70 — Lucide, grid 24, sem escala fixa |
| Tokens do Button | 48 — 40 alias, 8 transparentes, 0 valores soltos |
| Tokens do Icon Button | 42 — 34 alias, 8 transparentes, 0 valores soltos |
| Tokens do Tag | 39 — 33 alias, 6 transparentes, 0 valores soltos |
| Tokens do Avatar | 13 — 13 alias, 0 transparentes, 0 valores soltos |
| Tokens do Select | 31 — 31 alias, 0 transparentes, 0 valores soltos |
| Tokens do Checkbox | 22 — 22 alias, 0 transparentes, 0 valores soltos |
| Tokens do Radio | 21 — 21 alias, 0 transparentes, 0 valores soltos |
| Tokens do Switch | 20 — 20 alias, 0 transparentes, 0 valores soltos |

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

components/icon/
  icons/*.svg    # os 70 desenhos — Lucide, ISC (ver NOTICE); o resto do repo é MIT
  tokens.py      # camada de alias do Icon + portão de alias, gera tokens.json e o CSS
  icon.css       # o componente, escrito à mão — só caixa e tinta
  check.py       # portão do CSS: recusa valor literal em icon.css
  icons.py       # portão do desenho: recusa SVG fora da família, gera icons.json
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json

components/icon-button/
  tokens.py      # camada de alias do Icon Button + portão de alias, gera tokens.json e o CSS
  icon-button.css # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal em icon-button.css
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json

components/tag/
  tokens.py      # camada de alias do Tag + portão de alias + portão de contraste, gera tokens.json e o CSS
  tag.css        # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal em tag.css
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json

components/avatar/
  tokens.py      # camada de alias do Avatar + portão de alias + portão de contraste, gera tokens.json e o CSS
  avatar.css     # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal em avatar.css
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json

components/select/
  tokens.py      # camada de alias do Select + portão de alias + portão de contraste, gera tokens.json e o CSS
  select.css     # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal e token órfão em select.css
  a11y.py        # QA de acessibilidade + contrato de marcação de formulário, gera a11y.json
  qa.py          # gera site/select-qa.html, a visualização da etapa 6

components/checkbox/
  tokens.py      # camada de alias do Checkbox + portão de alias + portão de contraste, gera tokens.json e o CSS
  checkbox.css   # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal e token órfão em checkbox.css
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json
  qa.py          # gera site/checkbox-qa.html, a visualização da etapa 6

components/radio/
  tokens.py      # camada de alias do Radio + portão de alias + portão de contraste, gera tokens.json e o CSS
  radio.css      # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal e token órfão em radio.css
  a11y.py        # QA de acessibilidade + contrato de marcação da pergunta, gera a11y.json
  qa.py          # gera site/radio-qa.html, a visualização da etapa 6

components/switch/
  tokens.py      # camada de alias do Switch + portão de alias + portão de contraste, gera tokens.json e o CSS
  switch.css     # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal e token órfão em switch.css
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json
  qa.py          # gera site/switch-qa.html, a visualização da etapa 6

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
python3 components/icon/tokens.py    # tokens do Icon + portão de alias + CSS
python3 components/icon/check.py     # portão do CSS do Icon
python3 components/icon/icons.py     # portão do desenho + manifesto
python3 components/icon-button/tokens.py  # tokens do Icon Button + portão de alias + CSS
python3 components/icon-button/check.py   # portão do CSS do Icon Button
python3 components/tag/tokens.py     # tokens do Tag + portão de alias + portão de contraste + CSS
python3 components/tag/check.py      # portão do CSS do Tag
python3 components/avatar/tokens.py  # tokens do Avatar + portão de alias + portão de contraste + CSS
python3 components/avatar/check.py   # portão do CSS do Avatar
python3 components/select/tokens.py  # tokens do Select + portão de alias + portão de contraste + CSS
python3 components/select/check.py   # portão do CSS do Select + token órfão
python3 components/checkbox/tokens.py  # tokens do Checkbox + portão de alias + portão de contraste + CSS
python3 components/checkbox/check.py   # portão do CSS do Checkbox + token órfão
python3 components/radio/tokens.py  # tokens do Radio + portão de alias + portão de contraste + CSS
python3 components/radio/check.py   # portão do CSS do Radio + token órfão
python3 components/switch/tokens.py  # tokens do Switch + portão de alias + portão de contraste + CSS
python3 components/switch/check.py   # portão do CSS do Switch + token órfão
python3 site/site.py               # o site: Foundation + componentes
python3 components/icon/a11y.py      # QA do Icon — depois do site, ver abaixo
python3 components/icon-button/a11y.py    # QA do Icon Button — idem
python3 components/tag/a11y.py       # QA do Tag — idem
python3 components/avatar/a11y.py    # QA do Avatar — idem
python3 components/select/a11y.py    # QA do Select — idem
python3 components/checkbox/a11y.py  # QA do Checkbox — idem
python3 components/radio/a11y.py     # QA do Radio — idem
python3 components/switch/a11y.py    # QA do Switch — idem
python3 site/site.py               # de novo, para o site ler os a11y.json atualizados
```

Nesta ordem, e de qualquer diretório. O `export.py` vem antes do `css.py` por necessidade: o CSS copia a versão do `tokens.json`, que só o `export.py` regrava.

Os `a11y.py` são os únicos que rodam **depois** do site, e pelo mesmo motivo: além do
contraste, eles conferem o contrato de marcação no HTML que o site realmente emite —
contraste se prova no token, marcação só existe na saída renderizada. O do Icon cobra
`aria-hidden` versus `role="img"`; o do Icon Button cobra o `aria-label` obrigatório,
`aria-busy` sempre acompanhado de `aria-disabled`, e a ausência do atributo `disabled`; o do
Tag cobra que a tag não seja focável nem acionável e que o `aria-label` do X **inclua o rótulo**
— numa lista de seis filtros, seis botões chamados "Remover" são indistinguíveis por leitor de
tela; o do Avatar cobra que o invólucro seja `aria-hidden` OU `role="img"` com `aria-label`
(nunca os dois, nunca nenhum), que a foto tenha `alt=""` sempre, e que o ícone interno seja
sempre decorativo; o do Select cobra `<label for>` ligado ao campo, `aria-describedby` que existe
no erro e o placeholder como `<option value="">` selecionada; o do Checkbox cobra o input nativo
dentro do `<label>`, rótulo visível sem `aria-label`, glifos decorativos e nenhum atributo
`indeterminate` na marcação; o do Radio cobra a pergunta — todo `name` com duas opções ou mais,
dentro de um só `<fieldset>` com `<legend>` visível — e o erro no `fieldset`, nunca no radio; o do Switch cobra `role="switch"` só no input nativo,
rótulo visível, nada de `aria-checked`, `required` ou `aria-invalid`, e a bolinha decorativa. Cada um escreve seu `a11y.json`, que o site lê na próxima geração para montar
a aba de acessibilidade. As duas gerações convergem numa passada; não há loop.

## Os portões

Validação é parte do build, não checagem opcional. Cada camada tem o seu, e cada um aborta com saída diferente de zero:

| Portão | Onde | O que recusa |
|---|---|---|
| Contraste | `foundation/export.py` | Qualquer par de cor abaixo do mínimo WCAG. Exceções de marca são nomeadas uma a uma e nunca descem de 3:1. |
| Alias | `components/<c>/tokens.py` | Token de componente com valor próprio — hex, px, ou nome semântico inexistente. |
| CSS literal | `components/<c>/check.py` | Cor, comprimento ou peso literal dentro do CSS do componente. |
| Acessibilidade | `components/<c>/a11y.py` | Combinação renderizada (variante × estado × tema) fora do mínimo, medida contra o fundo efetivo. |
| Desenho | `components/icon/icons.py` | SVG fora da família: outro grid, outra espessura, cor cravada, ou `class` própria. O risco daquela pasta não é um valor errado — é um ícone de outra biblioteca entrando sem ninguém ver. |
| Marcação · Icon | `components/icon/a11y.py` | `.al-icon` no HTML emitido sem contrato de acessibilidade, ou com `aria-hidden` junto de um rótulo. |
| Marcação · Tag | `components/tag/a11y.py` | `.al-tag` no HTML emitido que seja `<button>`, tenha `role="button"` ou `tabindex`, ou cujo X esteja sem `type="button"`, sem `aria-label`, ou com um `aria-label` que não contenha o rótulo da tag. |
| Marcação · Icon Button | `components/icon-button/a11y.py` | `.al-icon-btn` no HTML emitido sem `aria-label`, com `aria-hidden` no próprio botão, com `aria-busy` solto sem `aria-disabled`, ou usando o atributo `disabled`. Esse contrato não vive no CSS, então o portão de literal não alcança — é aqui que ele é cobrado. |
| Token órfão | `components/select/check.py`, `components/checkbox/check.py`, `components/radio/check.py`, `components/switch/check.py` | Token declarado no `tokens.py` que o CSS do componente nunca consome — ou o CSS esqueceu de aplicar, ou o token não devia ter nascido. |
| Marcação · Select | `components/select/a11y.py` | Campo sem `<label for>` ligado ao `id`, erro sem `aria-describedby` que exista, placeholder que não seja a primeira `<option value="">` selecionada, seta sem contrato decorativo, ou `aria-label` havendo rótulo visível. |
| Marcação · Checkbox | `components/checkbox/a11y.py` | Checkbox fora de `<label class="al-checkbox">` ou sem `type="checkbox"`, `role="checkbox"` em qualquer tag, rótulo vazio ou `aria-label`, erro sem `aria-describedby` que exista, glifo sem contrato decorativo, ou `indeterminate` escrito como atributo. |
| Marcação · Radio | `components/radio/a11y.py` | Radio fora de `<label class="al-radio">` ou sem `type="radio"`, `role="radio"` em qualquer tag, rótulo vazio ou `aria-label`, radio sem `name` ou sozinho no seu `name`, pergunta fora de `<fieldset>` ou sem `<legend>`, `aria-invalid` no radio em vez do `fieldset`, erro sem `aria-describedby` que exista, ou ponto sem `aria-hidden`. |
| Marcação · Switch | `components/switch/a11y.py` | Switch fora de `<label class="al-switch">`, input sem `type="checkbox"` ou sem `role="switch"`, `role="switch"` em qualquer outra tag, `aria-pressed`, rótulo vazio ou `aria-label`, `aria-checked` no input, `required` ou `aria-invalid`, ou bolinha sem `aria-hidden`. Foi este portão que reprovou o switch de tema feito à mão do próprio site. |
| Marcação · Avatar | `components/avatar/a11y.py` | `.al-avatar` no HTML emitido com `aria-hidden` e `role="img"` juntos, ou nenhum dos dois; `role="img"` sem `aria-label`; a foto interna sem `alt=""`; ou o ícone interno sem `aria-hidden`/`focusable="false"`. |

## Arquitetura de tokens

Três camadas, cada uma com um trabalho:

1. **Primitiva** — escala de cor em OKLCH, uma única escada de lightness compartilhada por todas as famílias, ancorada na cor de marca. Nenhum componente consome esta camada direto.
2. **Semântica** — papel de uso (`bg-brand`, `text-secondary`, `border-focus`), com um valor por tema. É onde o tema é resolvido.
3. **Componente** — alias do semântico, um por papel do componente (`button-primary-bg-hover`). Só diverge para uma primitiva quando o componente exige. Nunca hex solto.

Em CSS, a camada de componente não tem bloco de tema — e não precisa. O tema troca no `:root`, que é o mesmo elemento onde os alias são declarados, então o `:root` re-substitui todos de uma vez.

> Substituição de custom property acontece no elemento onde ela é **declarada**, não no ponto de uso. Um alias declarado no `:root` desce já resolvido. Tematizar um container solto — e não o `:root` — exige re-declarar a camada dentro dele; é o que `site/site.py` faz para o playground.

**Nomenclatura:** o nome do token separa níveis com hífen (`bg-brand`, `button-primary-bg-hover`). No Figma, a mesma coisa vive em pasta dentro da collection do componente (`primary/bg-hover` na collection `4. Button`) — a barra é o mecanismo de agrupamento do painel de variáveis, não parte do nome do token.

**Nem todo token de código vira variável no Figma.** O Icon Button tem 42 tokens e 28 variáveis na collection `5. Icon Button`, e a diferença é deliberada. As oito tintas saem da collection `3. Icon ink`, que resolve por **modo** — um mecanismo que o CSS não tem, e por isso lá cada tinta precisa ser uma custom property concreta. Os quatro anéis de foco são *effect styles*, porque sombra não pode ser variável. E os dois `icon-size` apontam direto para a Foundation. O Button segue a mesma regra: 48 tokens, 40 variáveis. O Avatar tem 13 tokens e 10 variáveis na collection `7. Avatar` — a diferença são as três fontes (`Label/sm`, `Heading/xs`, `Heading/sm`), que são estilos de texto e não variáveis, mesma regra do Tag. O Select tem 31 tokens e 25 variáveis na collection `8. Select`; o Checkbox, 22 tokens e 20 variáveis na collection `9. Checkbox`; o Radio, 21 tokens e 19 variáveis na collection `10. Radio`; o Switch, 20 tokens e 18 variáveis na collection `11. Switch` — nos quatro a diferença são as fontes e os anéis de foco, que são estilos e não variáveis.

**Escala de ícone:** `icon-size` tem os degraus 16, 20, 24 e 32, nomeados pelo próprio valor — como o espaçamento, e pelo mesmo motivo: nome de camiseta obriga a renomear quando um degrau entra no meio. A escala nomeia os tamanhos recorrentes; ela não limita o componente `Icon`, que é vetorizado e vale em qualquer tamanho. O portão de CSS literal valida contra ela, então um tamanho novo dentro do DS é uma decisão consciente de uma linha.

## Pendências registradas

Coisas deliberadamente não construídas, anotadas para não voltarem como dúvida:

- **Escala de motion** — as durações no `button.css` e no `icon-button.css` são literais e aparecem no relatório do `check.py` como exceção consciente. O `tag.css` não entra nessa lista: ele não tem transição nem animação, porque o X não tem hover — por decisão.
- **Tooltip** — os cinco sistemas de referência pedem tooltip para botão só de ícone (o Primer sempre renderiza um; o Polaris diz que deve ser fornecido; o Spectrum define o tooltip justamente como o lugar do rótulo). Como o componente ainda não existe aqui, o `aria-label` vai sozinho: atende o leitor de tela, mas não o usuário vidente que não reconhece o ícone. É por isso que a regra de uso do Icon Button restringe o componente a ações universalmente reconhecíveis.
- **Alvo de toque do `sm`** — 36×36 passa o mínimo do WCAG 2.5.8 (24) e fica abaixo dos 44 que o Carbon recomenda. Não há expansão de área por pseudo-elemento, por decisão; a contrapartida é a regra de uso, que reserva o `sm` para densidade alta em interface de ponteiro.
- **Alvo de toque do X do Tag** — 16px no `sm` e 20px no `md`, abaixo dos 24 do WCAG 2.5.8. Mesma família de decisão do `sm` do Button, e mesma saída: regra de uso, não geometria — `sm` dismissível só em interface de ponteiro. O `a11y.py` do Tag mede e reporta, nunca reprova.
- **Unidade de tipografia** — a escala é em `px`. Atende o critério 1.4.4 (zoom do navegador escala `px`), mas não acompanha a preferência de tamanho de fonte do usuário. Migrar para `rem` é decisão de Foundation, não de componente.
- **Alto contraste forçado no Avatar** — no modo de alto contraste do sistema operacional o fundo é substituído e o círculo perde o limite visível. O Tag recolore uma borda que já existia; o Avatar não tem borda em variante nenhuma, e acrescentar uma só nesse modo seria inventar geometria fora do Figma. Medido e anotado, não resolvido às pressas.

## Contribuindo

Projeto em estágio inicial, mantido por [@guilhermedworakowski](https://github.com/guilhermedworakowski). Guia de contribuição chega quando o projeto tiver colaboradores externos ativos.

## Licença

[MIT](LICENSE) © 2026 Guilherme Domingues
