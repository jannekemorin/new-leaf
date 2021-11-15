reachable(Z, X) :- edge(X, Y), edge(Y, Z).
reachable(Y, X) :- edge(X, Y).

edge(1, 2).
edge(2, 3).