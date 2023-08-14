% neighbor/2 predicate to define neighbors (replace with your own logic)
neighbor(Node, Neighbor) :- eta(Node, Neighbor, _).
neighbor(Node, Neighbor) :- eta(Neighbor, Node, _).

get_cost(Node, Neighbor, Cost) :- eta(Node, Neighbor, Cost).
get_cost(Node, Neighbor,Cost) :- eta(Neighbor, Node, Cost).

calculate_cost([_],0).
calculate_cost([Head|[Second|Rest]],Cost):-
    get_cost(Head, Second, C1),
    calculate_cost([Second|Rest], CRest),
    Cost is C1 + CRest.

%Depth-first Search Implementation
depth_first_search(Start, Goal,Path):-
    dfs(Start, Goal, [Start], Path).

% dfs/4 Goal node found.
dfs(Goal, Goal,_,[Goal]).

% dfs/4 Recurvice depth search.
dfs(Start, Goal, Visited, [Start|Path]):-
    neighbor(Start, Node),
    not(member(Node,Visited)),
    dfs(Node, Goal, [Node|Visited], Path).


%Breadth-first Search Implementation
breadth_first_search(Start, Goal, Path) :-
    bfs([0-(Start, [Start])], Goal, RevPath),
    reverse(RevPath, Path).

% bfs/3 Goal node found.
bfs([_C-(Node, Path) | _], Node, Path).

% bfs/3Recursive case: Continue BFS
bfs([_C-(_Node, Path) | Rest], Goal, FinalPath) :-
    expand(Path, NewNodes),
    append(Rest, NewNodes, NewQueue),
    keysort(NewQueue, SortedQueue),
    bfs(SortedQueue, Goal, FinalPath).

% expand/2 predicate to generate neighboring nodes
expand([Node|Path], Neighbors) :-
    findall(C-(Neighbor,[Neighbor | [Node|Path]]),
            (neighbor(Node, Neighbor), not(member(Neighbor, Path)), calculate_cost([Neighbor | [Node|Path]], C)),
            Neighbors).


% A* Search Implementation
a_star_search(Start, Goal, Path) :-
    heuristic(Start, Goal, F),
    a_star([F-(0, Start, [Start])], Goal, RevPath),
    reverse(RevPath, Path).

% Base case: Goal node found
a_star([_F-(_G, Node, Path) | _], Node, Path).

% Recursive case: Continue A* search
a_star([_F-(G, _Node, Path) | Rest], Goal, FinalPath) :-
    expand(Path, NewNodes, G, Goal),
    append(Rest, NewNodes, NewQueue),
    keysort(NewQueue, SortedQueue),
    a_star(SortedQueue, Goal, FinalPath).

% expand/5 predicate to generate neighboring nodes with cost
expand([Node|Path], Neighbors, G_prev, Goal) :-
    findall(F-(G, Neighbor, [Neighbor | [Node|Path]]),
            (neighbor(Node, Neighbor), not(member(Neighbor, Path)),
             calculate_cost([Neighbor|[Node|Path]], Cost),
             heuristic(Neighbor, Goal, H),
             G is G_prev + Cost, F is G + H),
            Neighbors).

% Heuristic function to calculate the estimated distance between nodes using latitude and longitude.
heuristic(Node, Destination, Heuristic) :-
    location(Node, Lat1, Lon1),
    location(Destination, Lat2, Lon2),
    haversine_distance(Lat1, Lon1, Lat2, Lon2, Heuristic).

% Convert degrees to radians
degrees_to_radians(Degrees, Radians) :-
    Radians is Degrees * (pi / 180).

% Haversine formula to calculate the distance between two points on Earth
haversine_distance(Lat1, Lon1, Lat2, Lon2, Distance) :-
    degrees_to_radians(Lat1, Lat1Rad),
    degrees_to_radians(Lon1, Lon1Rad),
    degrees_to_radians(Lat2, Lat2Rad),
    degrees_to_radians(Lon2, Lon2Rad),
    DLat is Lat2Rad - Lat1Rad,
    DLon is Lon2Rad - Lon1Rad,
    A is sin(DLat / 2) ** 2 + cos(Lat1Rad) * cos(Lat2Rad) * sin(DLon / 2) ** 2,
    C is 2 * atan2(sqrt(A), sqrt(1 - A)),
    Radius is 6371,  % Earth's radius in kilometers
    Distance is Radius * C.
