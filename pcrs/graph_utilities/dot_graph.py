import pydot


def layout_graph(challenges):
    """
    Layout a challenge graph.
    """
    graph = create_graph()
    add_challenges(challenges, graph)
    return str(graph.create(format="svg"))


def create_graph():
    """
    Create a challenge graph.
    """
    return pydot.Dot(graph_type="digraph",
                     strict=True,
                     rankdir='LR',
                     splines="ortho",
                     concentrate="true",
                     rank="same",
                     center="true",
                     mode="ipsep",
                     overlap="false",
                     height="10",
                     width="10",
                     nodesep=".5")


def add_challenges(challenges, graph):
    """
    Add challenges to a challenge graph.
    """
    keys = list(challenges.keys())
    for i in range(0, len(challenges)):
        label = add_newlines(challenges[keys[i]]['name'])
        root = create_node(label, str(keys[i]), graph)
        for li in challenges[keys[i]]['prerequisites']:
            label = add_newlines(challenges[li]['name'])
            node = create_node(label, str(li), graph)
            create_edge(root, node, graph)


def add_newlines(text):
    """
    Add newlines to text in order to decrease node size.
    """
    if len(text) > 8:
        words = text.split()
        text = ""
        word_counter = 0
        for word in words:
            word_counter += 1
            if len(word) > 5 or word_counter >= 2:
                word_counter = 0
                text = text + str(word) + "\n"
            else:
                text = text + str(word) + " "
    return text


def create_node(node_label, node_id, graph):
    """
    Create a node.
    """

    # This ensures that the id starts with a letter, should the input prefix ever be numeric.
    # HTML 4 strictly states that ids must start with an alphabetical character.
    node_id = "node-" + node_id

    node = pydot.Node(node_id,
                      shape="rect",
                      height=".4",
                      width="1",
                      margin="0.5, 0.05",
                      label=node_label,
                      id=node_id)
    node.set_shape("box")
    graph.add_node(node)
    return node


def create_edge(parent, child, graph):
    """
    Create an edge.
    """
    edge = pydot.Edge(child, parent, splines="ortho")
    graph.add_edge(edge)
    return edge