from pathlib import Path

from models.class_def import MethodMd
from python_mermaid.diagram import Link, MermaidDiagram, Node


class Diagram:
    """
    Diagram class that generates Mermaid code for the creation of diagrams
    Receives a map generate by the Analyzer class
    """

    def __init__(self, map: dict, diagram_title: str = "Workflow Diagram") -> None:
        self.map = map
        self.diagram_title = diagram_title
        self.diagram = self.__diagram_maker()

    def __diagram_maker(self, diagram_title: str = "Workflow Diagram") -> str:
        """
        Creates the Mermaid code based on the dictionary map of calls from Analyzer
        """
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
                    if isinstance(value, MethodMd):
                        value_node = Node(f"{value.class_object.name}.{value.name}")
                    else:
                        value_node = Node(value.name)
                    nodes_set.add(value_node)
                    links.append(Link(key_node, value_node))
                internal_func(values)

        internal_func(self.map)
        diagram = MermaidDiagram(diagram_title, list(nodes_set), links).__str__()
        return diagram

    def create_diagram_file(self, path: str | Path):
        """
        Creates a file that contains the entire diagram string
        Facilitating the process of copying the code to mermaid
        """
        with open(path, "w") as file:
            file.write(self.diagram)


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

    chart = MermaidDiagram(title="Little Women", nodes=the_march_family, links=family_links)

    print(chart)
