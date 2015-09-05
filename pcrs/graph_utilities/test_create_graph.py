import create_graph
import unittest
from bs4 import BeautifulSoup


class TestCreateGraph(unittest.TestCase):

    def setUp(self):
        self.graphInput = {34530: {'name': 'Intro', 'prerequisites': [], 'quest': '0'},
                           123452: {'name': 'System Calls', 'prerequisites': [34530], 'quest': '1'},
                           23453422: {'name': 'Synchronization', 'prerequisites': [34530], 'quest': '1123'},
                           34543543: {'name': 'Monitors and Examples', 'prerequisites': [23453422], 'quest': '1'},
                           34534534: {'name': 'Finishing Scheduling', 'prerequisites': [34543543], 'quest': '132123'},
                           23432234: {'name': 'Virtual Memory - Page Tables and TLBs', 'prerequisites': [34534534], 'quest': '1'},
                           43543434: {'name': 'MVM Implementation', 'prerequisites': [34534534], 'quest': '1'},
                           345343345: {'name': 'File Systems', 'prerequisites': [34534534], 'quest': '132123'},
                           28545640: {'name': 'Example File Systems', 'prerequisites': [23432234], 'quest': '1'},
                           234322342: {'name': 'Transactions', 'prerequisites': [23432234], 'quest': '132123'},
                           76745560: {'name': 'Security', 'prerequisites': [28545640], 'quest': '1'},
                           54345634: {'name': 'Deadlock', 'prerequisites': [76745560], 'quest': '1'},
                           34554332: {'name': 'Shell Programming', 'prerequisites': [54345634], 'quest': '1'},
                           34554343: {'name': 'Concurrency and Threads', 'prerequisites': [34554332], 'quest': '1'},
                           34543355: {'name': 'Disk I/O', 'prerequisites': [34554343], 'quest': '132123'},
                           32342333: {'name': 'Paging Design, Features', 'prerequisites': [34554343], 'quest': '1'},
                           43223444: {'name': 'Page Replacement Policies', 'prerequisites': [34554343], 'quest': '1'},
                           23432233: {'name': 'Paging', 'prerequisites': [43223444], 'quest': '1'},
                           34543243: {'name': 'Memory Management', 'prerequisites':  [34543355], 'quest': '1'},
                           23432344: {'name': 'Scheduling', 'prerequisites': [34543243], 'quest': '1'},
                           23442323: {'name': 'Locks, Semaphores, Monitors', 'prerequisites': [23432344], 'quest': '1'},
                           23443223: {'name': 'Threads & Intro to Synchronization', 'prerequisites': [23442323], 'quest': '1'},
                           43233342: {'name': 'Bootstrapping & Processes', 'prerequisites': [23443223], 'quest': '1'},

        }
        create_graph.output_graph(self.graphInput)
        graph_file = open('../ui/graph_gen.svg', 'r')
        file_data = graph_file.read().replace('\n', '')
        self.data = BeautifulSoup(''.join(file_data))

    def test_svg_length(self):
        self.assertGreater(len(str(self.data.svg)), 0)

    def test_defs_length(self):
        self.assertGreater(len(str(self.data.defs)), 0)

    def test_g_length(self):
        self.assertGreater(len(str(self.data.g)), 0)

    def test_path_length(self):
        self.assertGreater(len(str(self.data.path)), 0)

    def test_text_length(self):
        self.assertGreater(len(str(self.data.path)), 0)

    def test_edge_length(self):
        self.assertGreater(len(str(self.data.svg.findAll('g', {'class': 'edge'}))), 0)

    def test_node_length(self):
        self.assertEqual(len(self.data.svg.findAll('g', {'class': 'node'})), len(self.graphInput))

    def test_node_polygon_length(self):
        self.assertEqual(len(self.data.svg.findAll(lambda tag: tag.name == 'polygon' and
                                                   tag.findParent('g', {'class', 'node'}))), 0)

    def test_node_rect_length(self):
        self.assertEqual(len(self.data.svg.findAll(lambda tag: tag.name == 'rect' and
                                                   tag.findParent('g', {'class', 'node'}))), len(self.graphInput))
    def test_pattern_length(self):
        self.assertEqual(len(self.data.svg.findAll('pattern')), 2)

    def test_pattern_height(self):
        self.assertEqual(self.data.svg.findAll('pattern')[0].attrs['height'], '15')
        self.assertEqual(self.data.svg.findAll('pattern')[1].attrs['height'], '10')

    def test_pattern_widths(self):
        self.assertEqual(self.data.svg.findAll('pattern')[0].attrs['width'], '15')
        self.assertEqual(self.data.svg.findAll('pattern')[1].attrs['width'], '10')

    def test_pattern_ids(self):
        self.assertEqual(self.data.svg.findAll('pattern')[0].attrs['id'], 'play-image')
        self.assertEqual(self.data.svg.findAll('pattern')[1].attrs['id'], 'active-image')

    def test_image_height(self):
        self.assertEqual(self.data.svg.findAll('image')[0].attrs['height'], '23')
        self.assertEqual(self.data.svg.findAll('image')[1].attrs['height'], '14')

    def test_image_widths(self):
        self.assertEqual(self.data.svg.findAll('image')[0].attrs['width'], '23')
        self.assertEqual(self.data.svg.findAll('image')[1].attrs['width'], '14')

    def test_image_x_position(self):
        self.assertEqual(self.data.svg.findAll('image')[0].attrs['x'], '-1.35')
        self.assertEqual(self.data.svg.findAll('image')[1].attrs['x'], '3')

    def test_image_y_position(self):
        self.assertEqual(self.data.svg.findAll('image')[0].attrs['y'], '-1.35')
        self.assertEqual(self.data.svg.findAll('image')[1].attrs['y'], '3')

    def test_image_links(self):
        self.assertEqual(self.data.svg.findAll('image')[0].attrs['xlink:href'], './video.png')
        self.assertEqual(self.data.svg.findAll('image')[1].attrs['xlink:href'], './check.ico')

if __name__ == '__main__':
    unittest.main()