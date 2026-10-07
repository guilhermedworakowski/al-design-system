# AL Design System

Design system open source, do Figma ao código. Construído em público, uma camada de cada vez.

- **Licença:** MIT
- **Versão:** `0.17.2`
- **Figma:** biblioteca privada por enquanto — primitivas, semânticos e tokens de componente documentados abaixo

## Estado atual

A **Foundation** está fechada: primitivas de cor, camada semântica (dois temas), tipografia, espaçamento, radius, tamanho de ícone, elevação, anel de foco e motion — tudo gerado por código, nada digitado à mão no Figma ou na página de referência.

O **Button** é o primeiro componente a fechar as oito etapas do pipeline: auditado, tokenizado, documentado, codado, com playground e QA de acessibilidade.

O **Icon Button** é o segundo, e fechou as oito no mesmo formato. Ele é o Button sem rótulo visível — e essa ausência muda mais do que parece: o ícone passa a ser o único portador do sentido, o nome acessível vira contrato obrigatório em vez de recurso, e o piso de contraste desce de 4,5:1 para 3:1, porque o critério que vale é o 1.4.11 (não-textual) e não o 1.4.3. A consequência prática é que ele não tem nenhuma exceção de marca, enquanto o Button tem três — é a mesma cor medida contra um mínimo diferente.

O **Tag** é o terceiro, e é o primeiro do AL a fechar em **zero exceções de contraste carregando texto**. O Icon Button já fechava em zero, mas contra o piso de 3:1 do critério 1.4.11 — o portador do sentido dele é um ícone. Aqui o portador é um rótulo, então o piso é o 4,5:1 do 1.4.3, e a consequência mudou o escopo: o status Brand ficou de fora, porque branco sobre o laranja da marca dá 3,34:1 — o mesmo par que no Icon Button é aprovação. Ele também é o único componente sem nenhuma transição, e por isso o único sem pendência de escala de motion.

O **Icon** fechou sete das oito, pulando a documentação por decisão: ícone do AL vive dentro de acionável e quem carrega o sentido é o rótulo. O contrato de acessibilidade não foi pulado junto — ele virou portão, medido no HTML emitido, em vez de regra escrita.

O **Avatar** é o quarto, e fecha o Tier 1. Diferente dos outros três, os tipos dele não são uma escolha de variante — são uma cadeia: Photo se houver foto, Iniciais se houver nome, Icon como último recurso, nessa ordem, nunca uma caixa vazia. É também o menor portão de acessibilidade do sistema até agora: o fundo não varia por tipo nem por status, só por tema, então sobram quatro medições — e, como o Tag, fecha em zero exceções de contraste.

O **Select** abre o Tier 2 (formulário). É o `<select>` nativo: a lista aberta é desenhada pelo navegador, e o componente entrega o gatilho fechado — a distinção do Carbon entre *Select* e *Dropdown*/*ComboBox*. O que isso compra é teclado, leitor de tela e comportamento mobile sem uma linha de JavaScript. Ele marca o campo **opcional**, não o obrigatório, e traz duas exceções declaradas: a borda de repouso abaixo de 3:1, sustentada pela regra do rótulo visível, e o disabled abaixo de AA. Com ele entraram dois portões novos: token órfão (token declarado que o CSS nunca consome reprova) e o contrato de marcação de formulário.

O **Checkbox** é o segundo do Tier 2. É o `<input type="checkbox">` nativo com a caixa do AL pintada por cima, e o estado misto (indeterminado) só existe por JavaScript — não há atributo HTML. O Figma tem um eixo só de estado; as combinações que ele não desenha (marcado + foco, erro + marcado, marcado + desabilitado) são pintadas pelo código com os mesmos tokens. O componente não tem mensagem de erro de propósito: o formulário é obrigado a descrever o erro em texto, porque borda e rótulo vermelhos são só cor (WCAG 3.3.1 e 1.4.1). O portão dele mede contra três fundos — tela, faixa de seção e card — e mostra que, marcada, quem desenha a caixa é o preenchimento, não a borda.

O **Radio** é o terceiro do Tier 2. É o `<input type="radio">` nativo com o círculo do AL pintado por cima: setas, Tab entrando na pergunta uma vez só e "marcar um desmarca o outro" vêm do navegador. A diferença estrutural para o Checkbox é que o marcado **não pinta o fundo** — é borda laranja + ponto de 14px, com o anel branco entre os dois —, então saem `bg-checked` e o ícone, e entram `dot` e `dot-disabled`. Não existe componente de grupo, de propósito: a pergunta é `<fieldset>` + `<legend>` nativos, montados pela aplicação. E o **erro é da pergunta, não da opção**, como no Primer, no Carbon, no Spectrum e no Polaris: o `radio.css` lê `aria-invalid` no `fieldset`, nunca no radio, e marcar a pergunta uma vez acende todas as opções. Mesmas duas exceções declaradas do Checkbox.

O **Switch** é o quarto do Tier 2. É o `<input type="checkbox" role="switch">` nativo com o trilho do AL pintado por cima — o leitor de tela anuncia "chave, ligada", e Espaço alterna (Enter não, como no checkbox nativo). Ele liga ou desliga algo que **vale na hora**, sem botão "Salvar", e por isso não tem estado de erro: escolha que precisa ser validada é Checkbox (Spectrum, Polaris). Quando a ação falha, a bolinha volta ao estado real e a aplicação avisa em texto. Foi o primeiro componente a criar token na Foundation: `bg-thumb` e `bg-thumb-disabled`, semânticos com claro e escuro para a peça que desliza sobre um trilho. A bolinha desligada fica abaixo de 3:1 por decisão de design (`neutral-400` é o teto), sustentada pelo trilho laranja do ligado e pelo rótulo visível — três exceções declaradas no total. E é o primeiro componente que o próprio site consome: o switch de tema do trilho era um `<button role="switch">` feito à mão, o portão de marcação do Switch o reprovou, e ele passou a ser o componente.

O **Input** é o quinto do Tier 2: resposta livre de uma linha (texto, e-mail, URL, telefone). É o `<input>` nativo dentro de uma **caixa do AL** — borda, fundo e anel moram num invólucro, porque `<input>` não aceita filho e o prefixo e o sufixo precisam ficar dentro da borda. O estado do campo chega à caixa por `:has()`. Os afixos são `<label for>`: clicar em "www." foca o campo, o leitor de tela ouve "Site, www., .com" (`aria-labelledby`, solução do Polaris) e nenhum dos dois vai no envio. Não existe estado Active — campo de texto sempre casa `:focus-visible`, inclusive no clique, e a medição no Chromium confirmou. É o primeiro componente com **read-only**, e ele não é isento de contraste como o disabled: o texto é o mesmo do campo editável, o placeholder some (daria 4,21:1) e o read-only vazio mostra "—". O contador só fica vermelho quando o erro **é** o limite, e o limite não trava a digitação — sem `maxlength`, divergência consciente do Carbon com precedente no GOV.UK. Duas exceções declaradas: borda de repouso e de read-only abaixo de 3:1, sustentadas pelo rótulo visível, e disabled abaixo de AA. Senha vira o componente Password.

O **Textarea** é o sexto do Tier 2: resposta livre de várias linhas (descrição, comentário, justificativa). É o Input sem prefixo e sufixo — mesmos sete estados, mesmas cores, mesmas duas exceções —, e a ausência dos afixos muda a estrutura: a própria `<textarea>` nativa é a caixa, então o estado é lido direto nela, sem invólucro e sem `:has()`, e o puxador e a barra de rolagem são dela. A altura vem do atributo `rows`: três linhas (96px) são o padrão **e o piso** — um `min-height` segura um `rows` menor e segura o puxador —, e o formulário pede mais linhas quando espera resposta longa, como manda o GOV.UK. O `check.py` ganhou um portão novo: o 3 do CSS e o `ROWS` do `tokens.py` são o mesmo número em dois lugares e reprovam se divergirem. Altura fixa: o texto rola em vez de crescer (Carbon), redimensiona só na vertical, e o disabled não redimensiona. Enter quebra a linha e nunca envia. Com ele, a Foundation passou a declarar `color-scheme` também quando o tema é forçado por `data-theme` — sem isso, puxador e barra de rolagem seguiam o sistema e não a página.

O **Password** é o sétimo do Tier 2, e entrou no roadmap no lugar do Date picker: senha existe em todo sistema, data só em alguns. É o `<input type="password">` nativo numa caixa como a do Input, com o **olho** dentro da borda — um `<button>` de verdade, com anel de foco próprio, circular e sempre o padrão, mesmo com o campo em erro: o anel diz onde está o foco, e o erro é do campo. O ícone mostra a ação (olho = mostrar, olho cortado = esconder), e qual aparece é lido do `type` do campo, sem classe. É o **primeiro componente com JavaScript próprio**: o `password.js` revela o botão (sem script, o olho não existe — solução do GOV.UK), alterna `type` e nome anunciado ("Mostrar senha" / "Ocultar senha"), e esconde a senha de novo quando o formulário é enviado. Sem read-only, sem contador, sem `maxlength`, sem marca de opcional: o Password é sempre obrigatório, e os requisitos ficam no formulário, acima do campo, para serem lidos **antes** de errar (Polaris). O alvo do olho é 24×24 — o mínimo exato do WCAG 2.5.8. Mesmas duas exceções do Input.

Todo input do Tier 2 tem **um tamanho só**, por regra.

O **Divider** abre o Tier 3 (estrutura). É o `<hr>` nativo, horizontal ou vertical, desenhado como **borda** de uma caixa de espessura zero — e não como fundo — para continuar visível no modo de alto contraste do sistema. Uma espessura (1px) e uma cor, sem tamanho, sem estado e sem margem: o comprimento vem do contêiner e o espaço em volta é do layout. O padrão é **anunciado** ("separador"); decorativo é `aria-hidden="true"`, a vertical anunciada leva `aria-orientation="vertical"` e, dentro de lista, a linha é `<li role="separator">`, porque `<ul>` só aceita `<li>`. A linha fica abaixo de 3:1 em toda superfície e isso é **exceção declarada**, sustentada pela regra de uso de que ela nunca é a única pista do agrupamento — mas o portão tem um segundo julgamento, que reprova linha da mesma cor do fundo. Foi ele que pegou o `border-subtle` original **invisível** sobre card e modal no tema escuro (`neutral-800` sobre `neutral-800`); a cor virou `border-default`, só no Divider. O portão de marcação dele é o primeiro a ler a **árvore** do HTML, não só atributos: recusa divisor no começo ou no fim do contêiner, dois seguidos e `<hr>` solto dentro de lista.

O **Card** é o segundo do Tier 3: um contêiner para um assunto que se lê ou se resolve sozinho. Três tipos (Filled, Border, Elevated), três paddings (24, 16, 8), estático ou clicável. O fundo é `bg-surface-raised`, porque no tema escuro quem separa o card da página é a superfície que clareia, não a sombra. A borda do Border é desenhada **fora** da caixa, como o stroke outside do Figma: uma sombra de 1px que não ocupa espaço, e por isso os três tipos medem igual. Borda, anel de foco e elevação vivem em três camadas internas de `box-shadow` empilhadas numa ordem fixa — é assim que o Elevated com foco mantém a sombra, coisa que o Figma não consegue mostrar. O card clicável é um **link de verdade no título**, esticado sobre o card por um pseudo-elemento: o card inteiro é o alvo, mas o leitor de tela anuncia só o título, e nada mais clicável pode morar dentro dele. Não existe card desabilitado nem pressionado. Duas exceções declaradas: a borda em repouso abaixo de 3:1 e o fundo que mal se separa da página — as duas sustentadas pela regra de que o card se reconhece pelo conteúdo, e pela de que o Filled só fica sobre `bg-surface`. O portão de acessibilidade reprova o card **invisível**, sem nada que o separe da página.

O **Tab** é o terceiro do Tier 3 e o primeiro componente do AL com **script próprio**. Ele serve a dois usos com o mesmo visual: trocar o conteúdo na mesma tela, com o padrão de abas da APG (`role="tablist"`, uma parada de Tab, setas, Home e End), ou navegar entre páginas, como lista de links dentro de `<nav>` com `aria-current="page"` — nunca `role="tab"` num link, que promete um painel que não existe. Dois tipos, definidos no **grupo** e não na aba, para um grupo nunca misturar os dois: **Line**, em que a linha laranja marca a selecionada e o rótulo fica no preto principal, e **Square**, em que a selecionada é um bloco tonal que vai para a marca no hover e no pressed. A selecionada sai de `aria-selected` ou de `aria-current`, nunca de uma classe. O `tab.js` liga todo `.al-tabs[role="tablist"]`: só a aba aberta entra no Tab, as setas trocam de aba e dão a volta, `data-activation="manual"` faz as setas só moverem o foco, e o painel que sai é escondido, nunca apagado. A aba aberta pelo próprio clique não pinta o pressed de selecionada até o próximo aperto, porque o Safari ainda a considera apertada quando o clique a seleciona. No máximo dois níveis: Line por fora, Square por dentro. Um tamanho, sem desabilitado. Quatro exceções declaradas: a seleção tonal, que no escuro se distingue só pelo matiz e é paga pela regra de o painel começar com um título igual ao rótulo; a linha cinza, que é só trilho; e duas da marca herdadas do Button. O portão reprova a seleção **indistinguível** — a selecionada pintada igual à não selecionada no mesmo estado.

O **Accordion** é o quarto do Tier 3 e volta ao nativo: é o `<details>` com o `<summary>`, e por isso não tem script — o navegador abre, fecha, responde a Enter e Espaço e anuncia "recolhido" ou "expandido". Um item só, sem componente de grupo: a pilha são itens lado a lado, e o espaço entre eles é do layout, como no Radio. Vários abertos por padrão; um por vez só quando os itens são alternativas, com o mesmo `name` em cada `<details>`. Só o cabeçalho reage — hover, pressed e o anel de foco, que sobe uma camada para o conteúdo aberto não cobrir a base dele —, e o conteúdo fica parado no fundo de repouso. O título é visual: nada de `<h3>` dentro do `<summary>`, porque em parte dos leitores de tela ele sai da lista de títulos; quem precisa ser achado por título ganha um título de verdade antes da pilha. O chevron espelha em 120ms e a altura não anima. Um tamanho, sem desabilitado. Ele trouxe dois semânticos novos para a Foundation, `bg-hover-raised` e `bg-active-raised`: o item mora na superfície elevada, e no escuro o `bg-hover` comum era a mesma cor dela — o hover sumia. Duas exceções declaradas: a divisória entre cabeçalho e conteúdo, que só separa, e o fundo do item, que mal se separa da página e por isso mora sobre `bg-surface`. O portão de tokens trava a regressão: hover e pressed precisam se distinguir do repouso nos dois temas.

**Motion** entrou no 0.17.1 e fechou no 0.17.2. A curva depende do tipo da ação — entrada desacelera (`ease-out`), saída acelera (`ease-in`) — e a duração, do porte de quem se move: `panel` (300ms) para o que cobre a tela, `popup` (200ms) para o que aparece pequeno por cima dela, `feedback` (120ms) para a resposta de um controle ao ponteiro. A duração leva o nome do porte (ou do papel) e não do componente, para um Dialog ou Sheet futuro achar o degrau sem token novo. Os 12 componentes com transição usam o mesmo par: a base declara a curva de saída e um bloco `ENTRADA` troca para a de entrada nos estados de destino, porque o CSS usa a curva do estado para onde a transição vai. O spinner é loop e tem tokens próprios (700ms, 2400ms sob movimento reduzido, curva linear). Nenhum componente escreve duração nem curva à mão. Sob `prefers-reduced-motion` o componente zera a transição, e não existe token para isso.

| | |
|---|---|
| Primitivas de cor | 66 (6 famílias × 11 degraus) |
| Tokens semânticos | 53 × 2 temas |
| Tokens de motion | 8 — cinco durações (`feedback` 120ms, `popup` 200ms, `panel` 300ms, `spinner` 700ms, `spinner-reduced` 2400ms) e três curvas (`enter` ease-out, `exit` ease-in, `spinner` linear); os 12 componentes com transição consomem |
| Pares de contraste validados | 84 — 81 em AA pleno, 3 exceções de marca nomeadas, 0 abaixo do piso |
| Componentes prontos | 15 (Button, Icon Button, Tag, Avatar, Select, Checkbox, Radio, Switch, Input, Textarea, Password, Divider, Card, Tab, Accordion) |
| Ícones | 70 — Lucide, grid 24, sem escala fixa |
| Tokens do Button | 48 — 40 alias, 8 transparentes, 0 valores soltos |
| Tokens do Icon Button | 42 — 34 alias, 8 transparentes, 0 valores soltos |
| Tokens do Tag | 39 — 33 alias, 6 transparentes, 0 valores soltos |
| Tokens do Avatar | 13 — 13 alias, 0 transparentes, 0 valores soltos |
| Tokens do Select | 31 — 31 alias, 0 transparentes, 0 valores soltos |
| Tokens do Checkbox | 22 — 22 alias, 0 transparentes, 0 valores soltos |
| Tokens do Radio | 21 — 21 alias, 0 transparentes, 0 valores soltos |
| Tokens do Switch | 20 — 20 alias, 0 transparentes, 0 valores soltos |
| Tokens do Input | 33 — 33 alias, 0 transparentes, 0 valores soltos |
| Tokens do Textarea | 32 — 32 alias, 0 transparentes, 0 valores soltos |
| Tokens do Password | 29 — 29 alias, 0 transparentes, 0 valores soltos |
| Tokens do Divider | 2 — 2 alias, 0 transparentes, 0 valores soltos |
| Tokens do Card | 19 — 19 alias, 0 transparentes, 0 valores soltos |
| Tokens do Tab | 21 — 21 alias, 0 transparentes, 0 valores soltos |
| Tokens do Accordion | 13 — 13 alias, 0 transparentes, 0 valores soltos |

O plano de evolução completo — divisão de trabalho, pipeline por componente e roadmap em tiers — está no [playbook](https://claude.ai/code/artifact/18a0c1ed-949c-4c8d-8906-93c21ed560a3).

## Instalação

O AL é consumido como pacote npm instalado direto deste repositório, sempre fixado numa tag. Ele não é publicado no registro do npm: o `"private": true` do `package.json` impede publicação acidental, e a instalação por Git não depende disso.

```bash
npm install github:guilhermedworakowski/al-design-system#v0.17.2
```

A tag no fim não é opcional. Sem ela, cada instalação puxa o que estiver na `main` naquele dia, e o produto muda sem que ninguém tenha decidido mudar. Com a tag, atualizar é uma decisão explícita: trocar o número, reinstalar e revisar.

### O que vem no pacote

Só a saída que um produto consome:

- `foundation/al-foundation.css` — primitivas, semânticos (claro e escuro), tipografia, espaçamento, radius, tamanho de ícone, elevação, anel de foco e motion
- `components/<c>/al-<c>-tokens.css` e `components/<c>/<c>.css` — tokens e CSS de cada componente
- `components/password/password.js` — o comportamento do olho do Password, o único componente com script
- `components/icon/icons/*.svg` e `icons.json` — os 70 ícones (Lucide, ISC — ver `components/icon/NOTICE`)
- `tokens.json` — a fonte da verdade, para quem quiser ler os tokens por código

Os scripts Python (geração e portões) não vão no pacote: eles são o processo que produz essa saída, e rodam aqui, não no produto.

### Importar

A ordem importa, e é sempre a mesma: Foundation, depois os tokens do componente, depois o CSS do componente.

```js
import 'al-design-system/foundation.css';
import 'al-design-system/components/button/al-button-tokens.css';
import 'al-design-system/components/button/button.css';
```

Importe só os componentes que o produto usa. A Foundation é obrigatória em qualquer caso: todo token de componente é alias de um token dela.

O Password precisa também do script, carregado uma vez por página. Ele liga sozinho todo `.al-password` presente no carregamento; conteúdo inserido depois chama `window.alPassword.init(elemento)`:

```js
import 'al-design-system/components/password/password.js';
```

### Marcação

O CSS não garante acessibilidade sozinho. Cada componente tem um contrato de marcação — escrito no topo do seu `.css` e cobrado pelo `a11y.py` no site deste repositório. Ao usar um componente num produto, siga esse contrato; o portão daqui não roda no HTML de lá.

### Tema

Claro e escuro já vêm na Foundation. Sem nada no `<html>`, o tema segue o sistema operacional (`prefers-color-scheme`). Para forçar um, carimbe o root:

```html
<html data-theme="dark">
```

O tema troca no `:root`. Tematizar um container isolado exige re-declarar a camada semântica dentro dele (ver "Arquitetura de tokens").

### Fontes

As fontes não vêm no pacote. A Foundation declara `Inter` e `JetBrains Mono` com fallbacks de sistema; carregar os arquivos é responsabilidade do produto — de preferência hospedados junto com ele, em vez de um serviço externo.

### Ícones

Os SVGs entram inline, com a classe `.al-icon` no próprio `<svg>` — `<img>` e `background-image` não herdam a cor do texto. Em bundlers baseados em Vite (Astro, por exemplo), o conteúdo do arquivo pode ser lido com o sufixo `?raw`:

```js
import arrowRight from 'al-design-system/components/icon/icons/arrow-right.svg?raw';
```

O arquivo `.svg` traz só o desenho: a classe `.al-icon` e o contrato de acessibilidade (`aria-hidden="true" focusable="false"` quando decorativo, `role="img"` com `aria-label` quando carrega sentido) são acrescentados por quem consome. Um componente de ícone no produto resolve isso num lugar só.

### Atualizar

1. Ler o que mudou na release (mensagem do commit `Release x.y.z`).
2. Trocar a tag no `package.json` do produto e rodar `npm install`.
3. Revisar o produto nos dois temas antes de publicar.

## Estrutura

```
foundation/
  color.py       # motor OKLCH -> sRGB, gamut mapping, contraste
  build.py       # camada semântica + portão de contraste (WCAG 2.1 AA)
  export.py      # gera tokens.json a partir de color.py + build.py e grava a versão no package.json
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

components/input/
  tokens.py      # camada de alias do Input + portão de alias + portão de contraste, gera tokens.json e o CSS
  input.css      # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal e token órfão em input.css
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json
  qa.py          # gera site/input-qa.html, a visualização da etapa 6

components/textarea/
  tokens.py      # camada de alias do Textarea + portão de alias + portão de contraste, gera tokens.json e o CSS
  textarea.css   # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal, token órfão e piso de linhas fora do ROWS
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json
  qa.py          # gera site/textarea-qa.html, a visualização da etapa 6

components/password/
  tokens.py      # camada de alias do Password + portão de alias + portão de contraste, gera tokens.json e o CSS
  password.css   # o componente, escrito à mão
  password.js    # o olho: revela o botão, alterna type e nome, esconde no envio
  check.py       # portão do CSS: recusa valor literal e token órfão em password.css
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json
  qa.py          # gera site/password-qa.html, a visualização da etapa 6

components/divider/
  tokens.py      # camada de alias do Divider + portão de alias + portão de contraste, gera tokens.json e o CSS
  divider.css    # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal e token órfão em divider.css
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json
  qa.py          # gera site/divider-qa.html, a visualização da etapa 6

components/card/
  tokens.py      # camada de alias do Card + portão de alias + portão de contraste, gera tokens.json e o CSS
  card.css       # o componente, escrito à mão
  check.py       # portão do CSS: recusa valor literal e token órfão em card.css
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json
  qa.py          # gera site/card-qa.html, a visualização da etapa 6

components/tab/
  tokens.py      # camada de alias do Tab + portão de alias + portão de contraste, gera tokens.json e o CSS
  tab.css        # o componente, escrito à mão
  tab.js         # o teclado do padrão de abas: roving tabindex, setas, Home, End, ativação manual
  check.py       # portão do CSS: recusa valor literal e token órfão em tab.css
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json
  qa.py          # gera site/tab-qa.html, a visualização da etapa 6

components/accordion/
  tokens.py      # camada de alias do Accordion + portão de alias + portão de contraste + estado distinto, gera tokens.json e o CSS
  accordion.css  # o componente, escrito à mão — <details>/<summary> nativo, sem script
  check.py       # portão do CSS: recusa valor literal e token órfão em accordion.css
  a11y.py        # QA de acessibilidade + contrato de marcação, gera a11y.json
  qa.py          # gera site/accordion-qa.html, a visualização da etapa 6

site/
  site.py        # gera index.html: o site — Foundation + componentes, navegação e playground
```

Arquivos `tokens.json`, `*.css` gerados e `site/index.html` são saída — versionados para consulta, mas nunca editados à mão. A versão do `package.json` também: o `export.py` a regrava a partir do `tokens.json`, então o número do release mora num lugar só.

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
python3 components/input/tokens.py  # tokens do Input + portão de alias + portão de contraste + CSS
python3 components/input/check.py   # portão do CSS do Input + token órfão
python3 components/textarea/tokens.py  # tokens do Textarea + portão de alias + portão de contraste + CSS
python3 components/textarea/check.py   # portão do CSS do Textarea + token órfão + piso de linhas
python3 components/password/tokens.py  # tokens do Password + portão de alias + portão de contraste + CSS
python3 components/password/check.py   # portão do CSS do Password + token órfão
python3 components/divider/tokens.py  # tokens do Divider + portão de alias + portão de contraste + CSS
python3 components/divider/check.py   # portão do CSS do Divider + token órfão
python3 components/card/tokens.py     # tokens do Card + portão de alias + portão de contraste + CSS
python3 components/card/check.py      # portão do CSS do Card + token órfão
python3 components/tab/tokens.py      # tokens do Tab + portão de alias + portão de contraste + CSS
python3 components/tab/check.py       # portão do CSS do Tab + token órfão
python3 components/accordion/tokens.py  # tokens do Accordion + portão de alias + portão de contraste + CSS
python3 components/accordion/check.py   # portão do CSS do Accordion + token órfão
python3 site/site.py               # o site: Foundation + componentes
python3 components/icon/a11y.py      # QA do Icon — depois do site, ver abaixo
python3 components/icon-button/a11y.py    # QA do Icon Button — idem
python3 components/tag/a11y.py       # QA do Tag — idem
python3 components/avatar/a11y.py    # QA do Avatar — idem
python3 components/select/a11y.py    # QA do Select — idem
python3 components/checkbox/a11y.py  # QA do Checkbox — idem
python3 components/radio/a11y.py     # QA do Radio — idem
python3 components/switch/a11y.py    # QA do Switch — idem
python3 components/input/a11y.py     # QA do Input — idem
python3 components/textarea/a11y.py  # QA do Textarea — idem
python3 components/password/a11y.py  # QA do Password — idem
python3 components/divider/a11y.py   # QA do Divider — idem
python3 components/card/a11y.py      # QA do Card — idem
python3 components/tab/a11y.py       # QA do Tab — idem
python3 components/accordion/a11y.py # QA do Accordion — idem
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
rótulo visível, nada de `aria-checked`, `required` ou `aria-invalid`, e a bolinha decorativa; o do Input cobra
o rótulo ligado, a mensagem de erro não vazia, os afixos no `aria-labelledby`, nenhum `maxlength`, contador com `aria-live` e read-only nunca vazio; o do Textarea cobra o mesmo sem os afixos, e mais a `<textarea>` nativa (nada de `contenteditable`) e `rows` de 3 ou mais; o do Password cobra o campo nascendo `type="password"`, `autocomplete` de senha, `spellcheck="false"` e `autocapitalize="none"`, e o olho como `<button type="button">` com `aria-controls` e `aria-label`, ícones decorativos e desabilitado junto com o campo; o do Divider cobra `<hr>` ou `<li role="separator">` (nunca `<hr>` solto em lista), separador sem texto, `aria-orientation` só na vertical, nunca focável, decorativo só por `aria-hidden="true"`, e nenhum divisor no começo ou no fim do contêiner nem dois seguidos; o do Card cobra título em `h1`…`h6`, exatamente um link dentro do título no card clicável (`<a href>` ou `<button type="button">`, com nome), nada mais clicável dentro dele, o card em si nunca acionável, `<li class="al-card">` só dentro de lista, nada de card dentro de card, nada de disabled e um tipo e um padding por card; o do Tab cobra o grupo de painel com nome, a aba como `<button type="button" role="tab">` ligada ao painel nos dois sentidos, exatamente uma selecionada e só ela fora do `tabindex="-1"`, a navegação em `<nav>` com links e no máximo um `aria-current`, no máximo dois níveis (Line por fora, Square por dentro), de 2 a 6 abas, o painel começando com o rótulo da aba, e amostra `aria-hidden` sempre `inert`; o do Accordion cobra o `<details>` nativo com o `<summary class="al-accordion__header">` como primeiro filho, um título com texto, nenhum `h1`…`h6` nem elemento interativo dentro do `<summary>`, ícones decorativos, nada de Accordion dentro de Accordion, nada de `role`, `aria-expanded`, `aria-controls` ou `tabindex` manuais, nada de disabled e exatamente um conteúdo depois do cabeçalho. Cada um escreve seu `a11y.json`, que o site lê na próxima geração para montar
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
| Token órfão | `components/select/check.py`, `components/checkbox/check.py`, `components/radio/check.py`, `components/switch/check.py`, `components/input/check.py`, `components/textarea/check.py`, `components/password/check.py`, `components/divider/check.py`, `components/card/check.py`, `components/tab/check.py`, `components/accordion/check.py` | Token declarado no `tokens.py` que o CSS do componente nunca consome — ou o CSS esqueceu de aplicar, ou o token não devia ter nascido. |
| Marcação · Select | `components/select/a11y.py` | Campo sem `<label for>` ligado ao `id`, erro sem `aria-describedby` que exista, placeholder que não seja a primeira `<option value="">` selecionada, seta sem contrato decorativo, ou `aria-label` havendo rótulo visível. |
| Marcação · Checkbox | `components/checkbox/a11y.py` | Checkbox fora de `<label class="al-checkbox">` ou sem `type="checkbox"`, `role="checkbox"` em qualquer tag, rótulo vazio ou `aria-label`, erro sem `aria-describedby` que exista, glifo sem contrato decorativo, ou `indeterminate` escrito como atributo. |
| Marcação · Radio | `components/radio/a11y.py` | Radio fora de `<label class="al-radio">` ou sem `type="radio"`, `role="radio"` em qualquer tag, rótulo vazio ou `aria-label`, radio sem `name` ou sozinho no seu `name`, pergunta fora de `<fieldset>` ou sem `<legend>`, `aria-invalid` no radio em vez do `fieldset`, erro sem `aria-describedby` que exista, ou ponto sem `aria-hidden`. |
| Marcação · Switch | `components/switch/a11y.py` | Switch fora de `<label class="al-switch">`, input sem `type="checkbox"` ou sem `role="switch"`, `role="switch"` em qualquer outra tag, `aria-pressed`, rótulo vazio ou `aria-label`, `aria-checked` no input, `required` ou `aria-invalid`, ou bolinha sem `aria-hidden`. Foi este portão que reprovou o switch de tema feito à mão do próprio site. |
| Marcação · Input | `components/input/a11y.py` | Campo sem `<label for>` de rótulo ligado ao `id`, erro sem `aria-describedby` para uma mensagem que exista e não esteja vazia, afixo fora do `aria-labelledby`, `aria-label` havendo rótulo visível, `maxlength` (o limite não trava a digitação), contador sem `aria-live`, ou read-only vazio. |
| Marcação · Textarea | `components/textarea/a11y.py` | Classe do campo fora de uma `<textarea>` nativa ou `contenteditable`, campo sem `<label for>` de rótulo, `rows` menor que 3, `id` repetido, erro sem `aria-describedby` para uma mensagem não vazia, `aria-label` havendo rótulo visível, `maxlength`, contador sem `aria-live`, ou read-only vazio. |
| Marcação · Password | `components/password/a11y.py` | Campo sem `<label for>` de rótulo, `id` repetido, `aria-label` havendo rótulo visível, `maxlength`, campo que não nasce `type="password"`, `autocomplete` que não seja `current-password` ou `new-password`, falta de `spellcheck="false"` ou `autocapitalize="none"`, erro sem mensagem não vazia, olho sem `type="button"` (enviaria o formulário), sem `aria-controls` no campo ou sem `aria-label`, ícone do olho sem contrato decorativo, ou campo desabilitado com o olho habilitado. |
| Marcação · Divider | `components/divider/a11y.py` | `.al-divider` que não seja `<hr>` ou `<li role="separator">`, `<hr>` filho direto de `<ul>`/`<ol>`, separador com texto, vertical anunciada sem `aria-orientation="vertical"` (ou horizontal com ela), `tabindex`, evento de clique ou papel que não seja `separator`, `aria-hidden` diferente de `"true"`, e divisor no começo ou no fim do contêiner ou dois seguidos. Também reprova a linha **invisível** — da mesma cor da superfície onde ela é colocada. |
| Marcação · Card | `components/card/a11y.py` | `.al-card__title` que não seja `h1`…`h6`; card clicável sem exatamente um `.al-card__link` dentro do título, link sem `href`, `<button>` sem `type="button"` ou sem nome; qualquer outro elemento interativo dentro do card clicável; o card em `<a>`/`<button>`, com `tabindex`, evento de clique ou papel de acionável; `.al-card__link` fora de card clicável; `<li class="al-card">` fora de lista; card dentro de card; `disabled`/`aria-disabled`; e tipo ou padding contraditórios. Também reprova o card **invisível** — sem borda, sem sombra e com o fundo igual ao da página. |
| Marcação · Tab | `components/tab/a11y.py` | Grupo de painel sem nome; aba que não seja `<button type="button" role="tab">` com `aria-selected`, ou sem `aria-controls` para um `tabpanel` ligado de volta; nenhuma ou mais de uma selecionada, ou `tabindex` inicial que não rola; navegação fora de `<nav>` com nome, aba que não seja `<a href>`, `role="tab"`/`aria-selected` em link ou mais de um `aria-current`; aba sem rótulo; `disabled`/`aria-disabled`; três níveis, ou Line dentro de Square; `<ul class="al-tabs">` com filho que não seja `<li>`; `id` repetido; menos de 2 ou mais de 6 abas; painel que não começa com o rótulo da aba; e amostra `aria-hidden` sem `inert`. Também reprova a seleção **indistinguível**. |
| Marcação · Accordion | `components/accordion/a11y.py` | `.al-accordion` que não seja `<details>`; `.al-accordion__header` fora de `<summary>` ou que não seja o primeiro filho; cabeçalho sem `__title` com texto; `h1`…`h6` ou elemento interativo dentro do `<summary>`; ícone sem `aria-hidden="true"`; Accordion dentro de Accordion; `role`, `aria-expanded`, `aria-controls` ou `tabindex` no `<details>` ou no `<summary>`; `disabled`/`aria-disabled`; e nenhum ou mais de um `__content` filho direto, ou conteúdo antes do cabeçalho. Também reprova o item **invisível** — fundo igual ao da página. |
| Piso de linhas | `components/textarea/check.py` | O multiplicador do `min-height` no `textarea.css` diferente do `ROWS` do `tokens.py` — o mesmo número escrito em dois lugares. |
| Marcação · Avatar | `components/avatar/a11y.py` | `.al-avatar` no HTML emitido com `aria-hidden` e `role="img"` juntos, ou nenhum dos dois; `role="img"` sem `aria-label`; a foto interna sem `alt=""`; ou o ícone interno sem `aria-hidden`/`focusable="false"`. |

## Arquitetura de tokens

Três camadas, cada uma com um trabalho:

1. **Primitiva** — escala de cor em OKLCH, uma única escada de lightness compartilhada por todas as famílias, ancorada na cor de marca. Nenhum componente consome esta camada direto.
2. **Semântica** — papel de uso (`bg-brand`, `text-secondary`, `border-focus`), com um valor por tema. É onde o tema é resolvido.
3. **Componente** — alias do semântico, um por papel do componente (`button-primary-bg-hover`). Só diverge para uma primitiva quando o componente exige. Nunca hex solto.

Em CSS, a camada de componente não tem bloco de tema — e não precisa. O tema troca no `:root`, que é o mesmo elemento onde os alias são declarados, então o `:root` re-substitui todos de uma vez.

> Substituição de custom property acontece no elemento onde ela é **declarada**, não no ponto de uso. Um alias declarado no `:root` desce já resolvido. Tematizar um container solto — e não o `:root` — exige re-declarar a camada dentro dele; é o que `site/site.py` faz para o playground.

**Nomenclatura:** o nome do token separa níveis com hífen (`bg-brand`, `button-primary-bg-hover`). No Figma, a mesma coisa vive em pasta dentro da collection do componente (`primary/bg-hover` na collection `4. Button`) — a barra é o mecanismo de agrupamento do painel de variáveis, não parte do nome do token.

**Nem todo token de código vira variável no Figma.** O Icon Button tem 42 tokens e 28 variáveis na collection `5. Icon Button`, e a diferença é deliberada. As oito tintas saem da collection `3. Icon ink`, que resolve por **modo** — um mecanismo que o CSS não tem, e por isso lá cada tinta precisa ser uma custom property concreta. Os quatro anéis de foco são *effect styles*, porque sombra não pode ser variável. E os dois `icon-size` apontam direto para a Foundation. O Button segue a mesma regra: 48 tokens, 40 variáveis. O Avatar tem 13 tokens e 10 variáveis na collection `7. Avatar` — a diferença são as três fontes (`Label/sm`, `Heading/xs`, `Heading/sm`), que são estilos de texto e não variáveis, mesma regra do Tag. O Select tem 31 tokens e 25 variáveis na collection `8. Select`; o Checkbox, 22 tokens e 20 variáveis na collection `9. Checkbox`; o Radio, 21 tokens e 19 variáveis na collection `10. Radio`; o Switch, 20 tokens e 18 variáveis na collection `11. Switch`; o Input, 33 tokens e 26 variáveis na collection `12. Input`; o Textarea, 32 tokens e 25 variáveis na collection `13. Textarea`; o Password, 29 tokens e 23 variáveis na collection `14. Password` — nos sete a diferença são as fontes e os anéis de foco, que são estilos e não variáveis. O Divider fecha sem diferença: 2 tokens e 2 variáveis na collection `15. Divider`. O Card tem 19 tokens e 13 variáveis na collection `16. Card`: o anel de foco e as três sombras são *effect styles* (`Focus-ring/Default`, `Elevation/2`, `Elevation/4`) e as duas fontes são estilos de texto.

**Escala de ícone:** `icon-size` tem os degraus 16, 20, 24 e 32, nomeados pelo próprio valor — como o espaçamento, e pelo mesmo motivo: nome de camiseta obriga a renomear quando um degrau entra no meio. A escala nomeia os tamanhos recorrentes; ela não limita o componente `Icon`, que é vetorizado e vale em qualquer tamanho. O portão de CSS literal valida contra ela, então um tamanho novo dentro do DS é uma decisão consciente de uma linha.

## Pendências registradas

Coisas deliberadamente não construídas, anotadas para não voltarem como dúvida:

- **Tooltip** — os cinco sistemas de referência pedem tooltip para botão só de ícone (o Primer sempre renderiza um; o Polaris diz que deve ser fornecido; o Spectrum define o tooltip justamente como o lugar do rótulo). Como o componente ainda não existe aqui, o `aria-label` vai sozinho: atende o leitor de tela, mas não o usuário vidente que não reconhece o ícone. É por isso que a regra de uso do Icon Button restringe o componente a ações universalmente reconhecíveis.
- **Alvo de toque do `sm`** — 36×36 passa o mínimo do WCAG 2.5.8 (24) e fica abaixo dos 44 que o Carbon recomenda. Não há expansão de área por pseudo-elemento, por decisão; a contrapartida é a regra de uso, que reserva o `sm` para densidade alta em interface de ponteiro.
- **Alvo de toque do X do Tag** — 16px no `sm` e 20px no `md`, abaixo dos 24 do WCAG 2.5.8. Mesma família de decisão do `sm` do Button, e mesma saída: regra de uso, não geometria — `sm` dismissível só em interface de ponteiro. O `a11y.py` do Tag mede e reporta, nunca reprova.
- **Unidade de tipografia** — a escala é em `px`. Atende o critério 1.4.4 (zoom do navegador escala `px`), mas não acompanha a preferência de tamanho de fonte do usuário. Migrar para `rem` é decisão de Foundation, não de componente.
- **Alto contraste forçado no Avatar** — no modo de alto contraste do sistema operacional o fundo é substituído e o círculo perde o limite visível. O Tag recolore uma borda que já existia; o Avatar não tem borda em variante nenhuma, e acrescentar uma só nesse modo seria inventar geometria fora do Figma. Medido e anotado, não resolvido às pressas.

## Contribuindo

Projeto em estágio inicial, mantido por [@guilhermedworakowski](https://github.com/guilhermedworakowski). Guia de contribuição chega quando o projeto tiver colaboradores externos ativos.

## Licença

[MIT](LICENSE) © 2026 Guilherme Domingues
