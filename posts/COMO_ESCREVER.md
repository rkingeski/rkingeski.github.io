# Como escrever um post

1. Crie um arquivo nesta pasta com o nome `AAAA-MM-DD-nome-curto.md`
   (ex.: `2026-11-03-aula-pipeline.md`). O `nome-curto` vira o endereço:
   `feed/aula-pipeline.html`.
2. Comece o arquivo com o cabeçalho entre `---`:

   ```
   ---
   titulo: Título do post
   resumo: Uma ou duas frases que aparecem na lista da aba Feed.
   rascunho: nao
   ---
   ```

   Com `rascunho: sim`, o post não aparece no site (bom para ir escrevendo).
   A data vem do nome do arquivo.
3. Depois do cabeçalho, escreva em Markdown: `## Seção`, `**negrito**`,
   `*itálico*`, listas com `-`, links `[texto](https://...)`, código entre
   crases e blocos de código com três crases, tabelas e imagens
   `![descrição](imagens/figura.png)` (coloque a imagem em `posts/imagens/`).
4. Rode `python3 build.py`. A lista da aba Feed e as páginas em `feed/` são
   geradas de novo (não edite os arquivos de `feed/` à mão).

Este arquivo (COMO_ESCREVER.md) é ignorado pelo build, porque não começa com data.
