import dot_graph as cg
from bs4 import BeautifulSoup
import random


def output_graph(challenges):
    """
    Creates a challenge graph and outputs the created SVG.
    """
    svg_graph = cg.layout_graph(challenges)

    # Beautiful Soup is used to manipulate the svg into a desired format, as GraphViz creates its own unique output.
    graph_soup = BeautifulSoup(''.join(svg_graph))

    # Since graphViz doesn't provide the svg defs we want, we need to append them.
    svg_defs = create_defs()
    graph_soup.svg.insert(0, svg_defs.defs)

    # svg polygons cannot be modified as well as svg rects can, mainly the rx and ry attributes, so the polygons
    # are replaced with rects. The javascript currently searches through svg rect elements, but can easily read
    # polygons if need be.
    replace_polygons(graph_soup)
    remove_titles(graph_soup)
    customize_quests(graph_soup, challenges)
    write_graph(graph_soup)


def replace_polygons(graph_soup):
    """
    Remove all svg polygon elements and replace them with svg rect elements.
    """
    for g in graph_soup.findAll('g', {'class': 'node'}):
        for poly in g.findAll('polygon'):

            # The coordinates for the new SVG rect are built from the existing polygons points.
            coordinates = poly['points'].split()
            x_position = float(coordinates[1].split(',')[0])
            y_position = float(coordinates[0].split(',')[1])
            width = abs(float(coordinates[2].split(',')[0]) - float(coordinates[0].split(',')[0]))
            height = abs(float(coordinates[2].split(',')[1]) - float(coordinates[0].split(',')[1]))
            rect = create_svg_rect(x_position, y_position, width, height)
            g.insert(1, rect.rect)
            poly.extract()


def customize_quests(graph_soup, challenges):
    """
    Customize Quest groupings by generating different strokes for each Quest.
    """
    keys = list(challenges.keys())
    quests = {}
    for g in graph_soup.findAll('g', {'class': 'node'}):
        text = []
        for t in g.findAll('text'):
            text.append(t.string)

        # As the nodes are split up, they need to be joined together to be compared.
        text = ''.join(text)

        # As the nodes have newlines and spaces inserted into them, they need to be taken out for comparison
        # against the string from the graph input.
        text = text.replace(' ', '').replace('\n', '')
        for i in range(0, len(challenges)):
            challenge_text = challenges[keys[i]]['name'].replace(' ', '').replace('\n', '')

            if text == challenge_text:
                if not challenges[keys[i]]['quest'] in quests:

                    # Generates the random CSS colour for each individual quest.
                    r = lambda: random.randint(0, 255)
                    colour = '#%02X%02X%02X' % (r(), r(), r())
                    quests[challenges[keys[i]]['quest']] = colour
                g.rect['stroke'] = quests[challenges[keys[i]]['quest']]


def create_svg_rect(x_position, y_position, width, height):
    """
    Create an svg rect.
    """
    return BeautifulSoup('<rect rx="20" ry="20" class="rect" x="' + str(x_position) +
                         '" y="' + str(y_position) +
                         '" width="' + str(width) +
                         '" height="' + str(height) +
                         '"></rect>')


def create_defs():
    """
    Create the SVG defs.
    """

    # SVG defs are used to add images to elements.
    svg_defs = BeautifulSoup('<defs></defs>')
    svg_defs.defs.append(BeautifulSoup('<pattern id="play-image" width="15" height="15"><image ' +
                                       'xlink:href="./video.png" x="-1.35" y="-1.35" width="23"' +
                                       'height="23" /></pattern>').pattern)
    svg_defs.defs.append(BeautifulSoup('<pattern id="active-image" width="10" height="10"><image ' +
                                       'xlink:href="./check.ico" x="3" y="3" width="14"' +
                                       'height="14"" /></pattern>').pattern)
    return svg_defs


def remove_titles(graph_soup):
    """
    Remove the title elements created by Graphviz.
    """
    titles = graph_soup.findAll('title')
    for title in titles:
        title.extract()


def write_graph(graph_soup):
    """
    Write the graph to a file.
    """
    # TODO: Change file when integrating into PCRS.
    f = open('../ui/graph_gen.svg', 'w')
    f.write(graph_soup.svg.prettify())
    f.close()
