# Zestaw 5

1. Generator tworzy sieć przepływową z N warstwami pośrednimi (N >= 2). W każdej warstwie pośredniej losuje od 2 do N wierzchołków. Łuki między kolejnymi warstwami zapewniają, że każdy wierzchołek poza ujściem ma łuk wychodzący do następnej warstwy, a każdy poza źródłem ma łuk wchodzący z poprzedniej warstwy. Następnie dodaje 2N unikatowych łuków losowych, bez łuków wchodzących do źródła i wychodzących z ujścia. Przepustowości są losowane z [1, 10].
2. Ford-Fulkerson wybiera najkrótsze ścieżki powiększające przez BFS, czyli działa w wariancie Edmondsa-Karpa. Uwzględnia łuki rezydualne pozwalające cofnąć część wcześniejszego przepływu.

## Uruchomienie

```console
python -m grafy set5 --layers 3 --seed 10 --draw output/zestaw5_flow.png
```

Wynik zawiera przepustowości, wartości przepływu na każdym łuku, ścieżki powiększające i wartość maksymalnego przepływu. Rysunek oznacza łuki jako `przepływ/przepustowość`.
