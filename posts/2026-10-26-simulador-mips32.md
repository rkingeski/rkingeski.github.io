---
titulo: Um simulador do MIPS32 para a aula de AOC
resumo: Uma ferramenta web para acompanhar, instrução por instrução, o caminho dos dados no processador monociclo e no pipeline.
rascunho: nao
---

Na disciplina de Arquitetura e Organização de Computadores, o datapath do MIPS
costuma aparecer como uma figura estática no slide. Para que a turma possa ver
os dados percorrerem o processador, montei um
[simulador didático do MIPS32](https://rkingeski.github.io/simulador-mips32/)
que roda direto no navegador.

## O que dá para fazer

- escrever um programa em assembly e executá-lo passo a passo;
- ver quais blocos e sinais de controle cada instrução ativa;
- comparar a versão monociclo com o pipeline de cinco estágios;
- observar *hazards* de dados e de controle, com e sem *forwarding*.

O código está no [GitHub](https://github.com/rkingeski/simulador-mips32).
