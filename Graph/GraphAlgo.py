import json
import math

from API.GraphAlgoInterface import GraphAlgoInterface
from Classes import DiGraph, Path, TagHeap


def permutator(elements):
    if len(elements) <= 1:
        yield elements

    else:
        for perm in permutator(elements[1:]):
            for i in range(len(elements)):
                yield perm[:i] + elements[0:1] + perm[i:]


class GraphAlgo(GraphAlgoInterface):

    def __init__(self, G: DiGraph = DiGraph()):
        self.graph = G

    def get_graph(self):
        return self.graph

    def load_from_json(self, json_str):
        self.graph = DiGraph()
        dicts = json.loads(json_str)
        for n in dicts["Nodes"]:
            self.graph.add_node(int(n['id']), tuple(map(lambda x: float(x), n['pos'].split(','))))

        for e in dicts["Edges"]:
            self.graph.add_edge(int(e['src']), int(e['dest']), float(e['w']))

        dicts = json.loads(json_str)
        nodes = dicts["nodes"]
        for n in nodes.keys():
            self.graph.add_node(int(nodes[n]['key']), tuple(nodes[n]['loc']))

        edges = dicts["edges"]
        for dests in edges.keys():
            self.graph.edges[int(dests)] = {int(dst): float(edges[dests][dst]) for dst in edges[dests].keys()}

    def isConnected(self):
        return self.DFS() and self.transpose().DFS()

    def transpose(self):
        g = DiGraph()

        for node in self.graph.nodes.values():
            g.add_node(node.key, node.loc)

            edges = self.graph.edges[node.key]

            for dst in edges.keys():
                g.add_edge(dst, node.key, edges[dst])

        return GraphAlgo(g)

    def clearTags(self):
        for node in self.graph.nodes.values():
            if node is not None:
                node.tag = 0

    def ArbitraryNode(self):
        return iter(self.graph.nodes).__next__()

    def DFS(self):
        if self.graph.v_size() < 2:
            return True

        self.clearTags()

        stack = [self.ArbitraryNode()]
        nodesReached = 0

        while len(stack) > 0:
            node = self.graph.nodes[stack.pop(0)]
            nodesReached += 1

            if node.tag != 2:
                edges = self.graph.edges[node.key]
                for dst in edges.keys():
                    if self.graph.nodes[dst].tag == 0:
                        stack.insert(0, dst)
                        self.graph.nodes[dst].tag = 1

            node.tag = 2

        return nodesReached == self.graph.v_size()

    def dijkstra(self, src, dst):
        if not (self.graph.nodes[src] and self.graph.nodes[dst]):
            return None

        self.clearTags()

        prevs = [node.key for node in self.graph.nodes.values()]
        dists = TagHeap(self.graph.v_size(), self.graph)
        dists.min = src
        dists.values[src] = 0
        finished = False

        while True:  # while heap isn't empty( a note for farther updates)
            edges = self.graph.edges[dists.min]

            curr = dists.min
            change = False
            for edge in edges.keys():
                relaxed = dists.relax(dists.get(curr) + edges[edge], edge)
                change = change or relaxed

                if relaxed:
                    prevs[edge] = curr

            dists.update_chosen(curr)
            if dists.min == -1:
                break

        if dists.get(dst) == math.inf:
            return None, None

        if src == dst:
            path = Path(self.graph)
            path.add(src)
            return path, dists.values

        path = Path(self.graph)
        curr = dst
        while curr is not src:
            path.add(curr)
            curr = prevs[curr]
        path.add(src)

        return path, dists.values

    def shortest_path(self, src, dst):
        path, dists = self.dijkstra(src, dst)

        if path is None:
            return math.inf, None

        return path.weight, path.rout

    def centerPoint(self):

        if self.graph.v_size() == 0:
            return None

        ind = self.graph.nodes[self.ArbitraryNode()].key
        minMax = math.inf

        if not self.isConnected():
            return ind, minMax

        it = self.graph.get_all_v().keys()
        for node in it:

            path, dists = self.dijkstra(node, node)
            Max = max(dists)

            if Max < minMax:
                minMax = Max
                ind = node

        return ind, minMax

    def TSP(self, destinations):
        if len(destinations) < 2:
            return destinations

        rout = Path(self.graph)

        # trying all possible options before giving up
        for perm in permutator(list(range(len(destinations)))):

            destinationShuffeled = [destinations[i] for i in perm]
            possible = True

            while len(destinationShuffeled) > 0:
                path, dists = self.dijkstra(destinationShuffeled[0], destinationShuffeled[1])

                if path is not None and path.weight is not math.inf:
                    rout.remove(last=True)
                    rout.merge(path)
                else:
                    possible = False
                    break

                dst = rout.getLast()
                destinationShuffeled = [i for i in destinationShuffeled if i not in path.rout]
                if len(destinationShuffeled) == 0:
                    break
                destinationShuffeled.insert(0, dst)

            if possible:
                return rout.rout, rout.weight

        return None, None

    def plot_graph(self) -> None:
        import matplotlib.pyplot as plt

        G = self.get_graph()

        LocData = [(node.loc[0], node.loc[1]) for node in G.get_all_v().values()]

        LocData = list(map(list, zip(*LocData)))
        x = LocData[0]
        y = LocData[1]

        plt.scatter(x, y, s=70)
        for src in G.get_all_v().keys():
            for dst in G.all_out_edges_of_node(src).keys():
                node = G.nodes[src]
                x = node.loc[0]
                y = node.loc[1]
                node = G.nodes[dst]
                dx = node.loc[0] - x
                dy = node.loc[1] - y

                plt.arrow(x, y, dx, dy, width=0.00005, shape='full', color='g', length_includes_head=True)
                plt.annotate(str(G.edges[src][dst]), (x, y), (x + 0.7 * dx, y + 0.7 * dy), fontsize=4)

        plt.show()
