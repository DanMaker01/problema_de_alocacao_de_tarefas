------------------------------------------------------------------------------

# Problema da designação, ou, criador de escala de trabalho 
------------------------------------------------------------------------------

## Variáveis de decisão:

$x_{ij}$ = 1 se a atividade $i$ é feita pelo trabalhador $j$ e 0 caso contrário. 

## Dados:

- Matriz de custo $C$
- Trabalhadores necessários cada dia $D$
- Quantidade de dias que cada trabalhador faz $E$


## Modelo :

## $min \sum\limits_{i=1}^{n} \sum\limits_{j=1}^{m} c_{ij} \cdot x_{ij} $

## s.a. 

## $\sum\limits_{j=1}^{m} x_{ij}=D$, $i=1,...,n$

## $\sum\limits_{i=1}^{n} x_{ij}=E$, $j=1,...,m$

## $x_{ij} \in \\{0,1\\}$
------------------------------------------------------------------------------

# À fazer:
 - checkbox para restrições para limitar uma sequencia máxima de horas trabalhadas
 - testar com escalas das tias do aloja
 - testar com escalas mensais
   - testar escalas comuns

 ------------------------------------------------------------------------------

# Feito:

- Semanal + interface

