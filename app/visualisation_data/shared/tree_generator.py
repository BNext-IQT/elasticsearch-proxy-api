# pylint: disable=dangerous-default-value, too-many-instance-attributes
"""
Common functions for processing tree structures
"""

from app.es_data import es_data


def get_nodes_index(parsed_tree_root, path=[]):
    """
    :param parsed_tree_root:
    :param path:
    :return:
    """
    nodes_index = {}
    for node_id, node in parsed_tree_root.items():
        path_to_node = path + [node_id]
        index_id = ';'.join(path_to_node)
        nodes_index[index_id] = node

        children = node.get('children')
        if children is not None:
            nodes_to_add = get_nodes_index(children, path_to_node)
            for key, value in nodes_to_add.items():
                nodes_index[key] = value

    return nodes_index


def load_tree_from_agg(raw_tree_root):
    """

    :param raw_tree_root:
    :return:
    """
    parsed_tree_root = {}
    for item in raw_tree_root:
        item_id = item['key']
        node = {
            'id': item_id
        }
        parsed_tree_root[item_id] = node

        children = item.get('children')
        if children is not None:
            child_buckets = children.get('buckets')
            if child_buckets is not None:
                if len(child_buckets) > 0:
                    node['children'] = load_tree_from_agg(child_buckets)

    return parsed_tree_root


def load_tree_from_hits(hits):
    """
    :param hits:
    :return:
    """
    parsed_tree_root = {}
    nodes_index = {}

    for hit in hits:

        node_id = hit['_id']
        # Add new child, or complete its data if I have already added it before
        node = nodes_index.get(node_id)
        if node is None:
            new_node = {
                'id': node_id,
                'label': hit['_source']['pref_name'],
            }
            nodes_index[node_id] = new_node
        else:
            node['label'] = hit['_source']['pref_name']

        current_node = nodes_index[node_id]

        # Now get the parent ID
        parent_node_id = hit['_source']['parent_go_id']
        # 2 things can happen:
        if parent_node_id is None:
            # 1: it's a root node, then I just add it to the root
            parsed_tree_root[node_id] = current_node
        else:
            # 2: it's NOT a root node
            # I know that a node with parent_node_id must exist, and that the current hit is its child
            parent_node = nodes_index.get(parent_node_id)
            if parent_node is None:
                # I haven't created it before, so let's create it
                new_parent_node = {
                    'id': parent_node_id,
                    'children': {
                        node_id: nodes_index[node_id]
                    }
                }
                nodes_index[parent_node_id] = new_parent_node
            else:
                # I created it before, so I just add the current node to its children
                if parent_node.get('children') is None:
                    parent_node['children'] = {}
                parent_node['children'][node_id] = current_node

    return parsed_tree_root


def generate_count_queries_parent_to_child(tree_root, query_generator, level=1, path=[]):
    """
    :param tree_root:
    :param query_generator:
    :param level:
    :param path:
    :return:
    """
    queries = {}
    for node_id, node in tree_root.items():

        path_to_node = path + [node_id]
        query_id = ';'.join(path_to_node)
        query_string = query_generator(path_to_node)

        queries[query_id] = {
            'query': query_string
        }
        children = node.get('children')
        if children is not None:
            queries_to_add = generate_count_queries_parent_to_child(children, query_generator, level + 1, path_to_node)
            for key, value in queries_to_add.items():
                queries[key] = value

    return queries


def get_node_and_descendancy(node):
    """

    :param node:
    :return:
    """
    node_and_descendancy = []
    children = node.get('children')
    if children is None:
        return [node]

    node_and_descendancy += [node]
    # pylint: disable=unused-variable
    for child_key, child in children.items():
        node_and_descendancy += get_node_and_descendancy(child)

    return node_and_descendancy


def fill_descendants_index(tree_root_node, descendants_index, path=[]):
    """

    :param tree_root_node:
    :param descendants_index:
    :param path:
    :return:
    """
    node_id = tree_root_node['id']
    path_to_node = path + [node_id]
    index_id = ';'.join(path_to_node)

    descendants_index[index_id] = []

    children = tree_root_node.get('children')
    if children is not None:

        for child_id, child in children.items():
            path_to_child = path_to_node + [child_id]
            child_index_id = ';'.join(path_to_child)

            descendants_index[index_id].append(child_id)
            fill_descendants_index(child, descendants_index, path_to_node)

            descendants_from_child = descendants_index[child_index_id]
            descendants_index[index_id] += descendants_from_child


def generate_count_queries_child_to_parent(tree_root_nodes, query_generator):
    """

    :param tree_root_nodes:
    :param query_generator:
    :return:
    """
    queries = {}
    descendants = {}
    root_id = 'Root'
    tree_root_node = {
        'id': root_id,
        'children': tree_root_nodes
    }
    fill_descendants_index(tree_root_node, descendants)

    for key, descendant_list in descendants.items():

        if key == root_id:
            continue

        query_key = key.replace(root_id + ';', '')
        node_id = query_key.split(';')[-1]
        query_string = query_generator(node_id, descendant_list)
        queries[query_key] = {
            'query': query_string
        }

    return queries


class TargetHierarchyTreeGenerator:
    """
    Class that generates hierarchies for targets
    """

    def __init__(self, index_name, es_query, query_generator, count_index):

        self.index_name = index_name
        self.es_query = es_query
        self.query_generator = query_generator
        self.raw_tree_root = None
        self.parsed_tree_root = {}
        self.count_queries = {}
        self.nodes_index = {}
        self.count_index = count_index

    def get_classification_tree(self):
        """
        :return:
        """

        es_response = es_data.get_es_response(self.index_name, self.es_query)

        self.raw_tree_root = es_response['aggregations']['children']['buckets']
        self.build_final_tree()

        return self.parsed_tree_root

    def build_final_tree(self):
        """
        :return:
        """

        self.parsed_tree_root = load_tree_from_agg(self.raw_tree_root)
        self.load_item_counts()

    def load_item_counts(self):
        """

        :return:
        """

        self.nodes_index = get_nodes_index(self.parsed_tree_root)
        self.count_queries = generate_count_queries_parent_to_child(self.parsed_tree_root, self.query_generator)
        self.execute_count_queries()
        self.add_counts_to_tree()

    def execute_count_queries(self):
        """

        :return:
        """

        target_classes = list(self.count_queries.keys())  # be sure to be consistent with the order

        m_search_array = []

        for target_class in target_classes:
            current_query_string = self.count_queries[target_class]['query']
            query = {
                "_source": False,
                "query": {
                    "query_string": {
                        "_name": current_query_string,
                        "query": current_query_string,
                    }
                },
                "track_total_hits": True
            }

            m_search_array.append({'index': self.count_index})
            m_search_array.append(query)

        responses = es_data.do_multisearch(body=m_search_array)['responses']

        i = 0
        for response in responses:
            class_name = target_classes[i]
            self.count_queries[class_name]['count'] = response['hits']['total']['value']
            i = i + 1

    def add_counts_to_tree(self):
        """

        :return:
        """

        for node_path_str, query in self.count_queries.items():
            self.nodes_index[node_path_str]['count'] = query['count']
            self.nodes_index[node_path_str]['query_string'] = query['query']


class GoSlimTreeGenerator(TargetHierarchyTreeGenerator):
    """
    This generates a tree directly by reading the nodes, not by using aggregations
    """
    # pylint: disable=super-init-not-called

    def __init__(self):
        self.index_name = 'chembl_go_slim'
        self.count_index = 'chembl_target'
        self.es_query = {
            "size": 1000,
            "from": 0
        }

        def generate_count_query(current_node_id, descendant_list):
            """
            :param current_node_id:
            :param descendant_list:
            :return:
            """
            all_queries = []
            for node_id in [current_node_id] + descendant_list:
                node_query = '_metadata.target_component.go_slims.go_id:("{class_name}")'.format(class_name=node_id)
                all_queries.append(node_query)

            return ' OR '.join(all_queries)

        self.query_generator = generate_count_query
        self.raw_tree_root = None
        self.parsed_tree_root = {}
        self.count_queries = {}
        self.nodes_index = {}

    def get_classification_tree(self):
        """

        :return:
        """

        es_response = es_data.get_es_response(self.index_name, self.es_query)

        self.raw_tree_root = es_response['hits']['hits']
        self.build_final_tree()

        return self.parsed_tree_root

    def build_final_tree(self):
        """

        :return:
        """
        self.parsed_tree_root = load_tree_from_hits(self.raw_tree_root)
        self.load_item_counts()

    def load_item_counts(self):
        """

        :return:
        """
        self.nodes_index = get_nodes_index(self.parsed_tree_root)
        self.count_queries = generate_count_queries_child_to_parent(self.parsed_tree_root, self.query_generator)
        self.execute_count_queries()
        self.add_counts_to_tree()
