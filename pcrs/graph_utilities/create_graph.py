import os
import graph_utilities.dot_graph as cg
from bs4 import BeautifulSoup


def output_graph(challenges):
    """
    Create a challenge graph and outputs the created SVG.
    """

    svg_graph_horizontal = cg.layout_graph(challenges, "LR")
    svg_graph_vertical = cg.layout_graph(challenges, "TB")

    # Beautiful Soup is used to manipulate the svg into a desired format, as GraphViz creates its own unique output.
    graph_soup_horizontal = BeautifulSoup(''.join(svg_graph_horizontal))
    graph_soup_vertical = BeautifulSoup(''.join(svg_graph_vertical))

    # Uncomment below for defs. Current graph does not need them.
    # Since graphViz doesn't provide the svg defs we want, we need to append them.
    # svg_defs_horizontal = create_defs()
    # svg_defs_vertical = create_defs()
    # graph_soup_horizontal.svg.insert(0, svg_defs.defs)
    # graph_soup_vertical.svg.insert(0, svg_defs.defs)

    # svg polygons cannot be modified as well as svg rects can, mainly the rx and ry attributes, so the polygons
    # are replaced with rects. The javascript currently searches through svg rect elements, but can easily read
    # polygons if need be.
    replace_polygons(graph_soup_horizontal)
    replace_polygons(graph_soup_vertical)

    remove_titles(graph_soup_horizontal)
    remove_titles(graph_soup_vertical)

    customize_quests(graph_soup_horizontal, challenges)
    customize_quests(graph_soup_vertical, challenges)

    write_graph(graph_soup_horizontal, 'horizontal')
    write_graph(graph_soup_vertical, 'vertical')


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

    # Non-dithering colors from: http://www.htmlgoodies.com/tutorials/colors/article.php/3479001
    colours = ["#33CCFF", "#00CC33", "#FF9999", "#996699", "#0066FF", "#009966", "#FFCC33",
               "#CC6699", "#33FF66", "#FFCCFF", "#FFCC99", "#FF9933", "#6699CC", "#6699FF"]

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
                    k = i
                    if i < len(colours):
                        k = i % len(colours)
                    colour = colours[k]
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


def write_graph(graph_soup, orientation):
    """
    Write the graph to a file.
    """
    svg = os.path.join(os.getcwd(),
            'resources/challenge_graph/ui/graph_gen_' + orientation + '.svg')
    f = open(svg, 'w')
    f.write(graph_soup.svg.prettify())
    f.close()
