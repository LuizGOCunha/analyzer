# Creating a simple flowchart diagram
from models.class_def import MethodMd
from python_mermaid.diagram import Link, MermaidDiagram, Node


def diagram_maker(map:dict):
    nodes_set = set()
    links = []

    def internal_func(map):
        nonlocal nodes_set
        nonlocal links
        for key, values in map.items():
            if isinstance(key, MethodMd):
                key_node = Node(f"{key.class_object.name}.{key.name}")
            else:
                key_node = Node(key.name)
            nodes_set.add(key_node)
            for value in values:
                value_node = Node(value.name)
                nodes_set.add(value_node)
                links.append(Link(key_node, value_node))
            internal_func(values)
    
    internal_func(map)
    return list(nodes_set), links

if __name__ == "__main__":
    # Family members
    meg = Node("Meg")
    jo = Node("Jo")
    beth = Node("Beth")
    amy = Node("Amy")
    robert = Node("Robert March")

    the_march_family = [meg, jo, beth, amy, robert]

    # Create links
    family_links = [
        Link(robert, meg),
        Link(robert, jo),
        Link(robert, beth),
        Link(robert, amy),
    ]

    chart = MermaidDiagram(
        title="Little Women",
        nodes=the_march_family,
        links=family_links
    )

    print(chart)