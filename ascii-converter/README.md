# ASCII Converter

Converte imagens em ASCII art. Imprime no terminal, salva como imagem em alta
resolução ou como `.txt`, e mantém uma galeria HTML local de tudo que você já
gerou.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependências: `numpy` e `pillow`.

## Uso

```bash
python3 ascii-converter.py <imagem> [largura] [opções]
```

Sem opções, imprime a arte no terminal:

```bash
python3 ascii-converter.py images/frieren.jpg 100
```

A `largura` é em caracteres (padrão: 100). Ajuste para caber no seu terminal —
100 costuma funcionar bem, 200 exige uma janela larga ou fonte pequena.

### Salvando

```bash
# PNG em output/, registrado na galeria
python3 ascii-converter.py images/frieren.jpg 250 -o

# PNG + TXT, alta resolução
python3 ascii-converter.py images/frieren.jpg 250 -o --text --font-size 18

# Caminho específico, visual de terminal
python3 ascii-converter.py images/space-man.jpg 200 -o arte.png --fg white --bg black
```

O `-o` sem argumento salva em `output/<nome>-ascii.png`. Passando um caminho,
salva onde você mandar.

### Qualidade

Dois parâmetros definem o resultado final, e eles fazem coisas diferentes:

- **`largura`** — quantos caracteres de largura, ou seja, quanto detalhe da
  imagem original é capturado. É a resolução real da arte.
- **`--font-size`** — o tamanho de cada caractere em pixels. Não adiciona
  detalhe nenhum, só deixa os glifos maiores e mais nítidos no arquivo.

Para máxima qualidade, suba os dois: `250 -o --font-size 18` gera um PNG de
~2800x3900, bom para impressão ou wallpaper.

### PNG ou TXT?

Não é um melhor que o outro — servem a coisas diferentes, e `--text` gera os
dois de uma vez:

| | PNG | TXT |
|---|---|---|
| Tamanho típico | ~1 MB | ~40 KB |
| Aparência | congelada, idêntica em qualquer lugar | depende da fonte de quem abre |
| Bom para | postar, imprimir, wallpaper | README, terminal, copiar e colar, editar |

Use PNG quando a aparência precisa ser garantida; TXT quando você quer os
caracteres de verdade. Como o TXT custa quase nada, `-o --text` é um bom padrão.

## Galeria

Toda conversão com `-o` registra a arte em `gallery.json` e regenera
`gallery.html`. Abra a página com duplo clique — ela funciona offline, sem
servidor.

```
ascii-converter/
├── images/            # imagens de origem
├── output/            # PNGs e TXTs gerados
├── gallery.json       # índice das artes
└── gallery.html       # a página
```

A galeria mostra as artes mais recentes primeiro, com largura, resolução, data e
links de download. Segue o tema claro/escuro do sistema.

Cada arte é indexada **pela imagem de origem**: reconverter `frieren.jpg` com
outros parâmetros atualiza o card existente em vez de acumular duplicatas. Isso
também significa que duas variantes da mesma foto (uma clara, uma escura)
compartilham um único card — a mais recente vence. Use `-o` com nomes distintos
para que ao menos os arquivos não se sobrescrevam.

Passe `--no-gallery` para gerar algo avulso sem registrar.

## Opções

| Flag | Efeito |
|---|---|
| `-o`, `--output [CAMINHO]` | Salva como imagem e registra na galeria. Sem argumento, vai para `output/` |
| `-t`, `--text` | Salva também o `.txt` ao lado da imagem |
| `--no-gallery` | Não atualiza a galeria nesta execução |
| `--font-size N` | Tamanho da fonte em pixels ao salvar (padrão: 16) |
| `--font CAMINHO` | Uma `.ttf` monoespaçada específica |
| `--contrast N` | De -10 a 10 (padrão: 10). Controla quantos glifos da rampa são usados |
| `--fg COR` | Cor do texto ao salvar (padrão: `black`) |
| `--bg COR` | Cor do fundo ao salvar (padrão: `white`) |

Cores aceitam nomes (`white`, `navy`) ou hex (`#1e1e24`).

## Como funciona

A imagem é convertida para escala de cinza e redimensionada para a largura
pedida, com a altura reduzida pela metade — glifos de texto são mais altos que
largos, e isso preserva a proporção. Cada pixel então vira o caractere
correspondente ao seu brilho numa rampa que vai de `$` (mais denso, escuro) até
espaço (mais claro).

Ao renderizar em imagem, cada caractere é desenhado individualmente na sua
posição da grade, em vez de uma linha inteira por vez, para que o alinhamento
não escorregue caso algum glifo tenha largura diferente na fonte.

A fonte padrão é a DejaVu Sans Mono do sistema, com fallback para Liberation
Mono. Se nenhuma for encontrada, use `--font` para apontar uma.
