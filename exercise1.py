from glob import glob
from textutils import tokenize_document
from os.path import basename
from queryparser import process_ast, parse_query
from queryparser import ParseException


class ReverseIndex:

    def __init__(self, files):

        # we use positive integers for normal posting lists,
        # and negative integers for negated postings lists.
        # since -0 == 0, we start the index with 1
        self._document_index = 1
        self._documents = {}
        self._index = {}
        self._files = []

        for file in files:
            self.add_document(file)

    def __getitem__(self, item):
        # special case if the item is negated: we return ('NEGATED', lookup(item))
        if item.startswith('-'):
            return self.negate(self._index[item[1:]])
        if item in self._index:
            return self._index[item]
        else:
            return []

    def add_document(self, path):
        file_name, file_id = self.filename(path), self._document_index
        self._documents[self._document_index] = self.filename(path)
        for token in tokenize_document(path):
            if token not in self._index:
                self._index[token] = list()
            if file_id not in self._index[token]:
                self._index[token].append(file_id)
        self._document_index += 1

    def execute_query(self, query):
        """
        Execute a boolean query on the inverted index. This method should return a
        list of document ids which satisfy the query. The list does not need to be
        in a particular order.
        """
        try:
            ast = parse_query(query)
        except ParseException as e:
            print("Failed to parse query '%s':\n" % query, e)
            return []

        # flatten query AST
        flat = process_ast(ast)

        matches = self.parse(flat)
        if not matches:
            return []

        return [self._documents[index] for index in matches]

    def parse(self, flat):
        if isinstance(flat, str):
            return self[flat]
        elif flat.op == 'LOOKUP':
            print(flat.args[0]) # TODO matching NOT Brutus should fail with this error
            if flat.args[0].startswith('-'):
                raise NotImplementedError('Lookup of negated terms not supported.')
            return self[flat.args[0]]
        op = flat.op
        # we are at a leave

        args = [self.parse(e) for e in flat.args]
        if op == 'AND':
            return intersect_multiple(args)
        elif op == 'OR':
            return union_multiple(args)

    @staticmethod
    def filename(path):
        return basename(path)

    @staticmethod
    def negate(arg):
        return [-e for e in arg]


def and_not(p1, p2):
    """evaluates p1 AND NOT p2"""
    p2 = ReverseIndex.negate(p2)
    x, y = 0, 0
    solution = []
    while True:

        # TODO
        if x >= len(p1):
            break
        elif y >= len(p2):
            solution = solution + p1[x:]
            break

        if p1[x] < p2[y]:
            solution.append(p1[x])
            x += 1
        elif p1[x] == p2[y]:
            x += 1
            y += 1
        elif p1[x] > p2[y]:
            y += 1

    return solution


def intersect(p1, p2):
    """
    Method to compute the intersection of two postings lists.  Takes two
    postings lists as arguments and returns the intersection.
    """

    # check for AND NOT
    if p1[0] < 0:
        # both are negated
        if p2[0] < 0:
            raise NotImplementedError('NOT p1 AND NOT p2 is not supported')
        # p1 inverted, p2 is not inverted
        return and_not(p2, p1)
    elif p2[0] < 0:
        return and_not(p1, p2)

    x, y = 0, 0
    solution = []
    while True:

        if x >= len(p1) or y >= len(p2):
            break

        if p1[x] < p2[y]:
            x += 1
        elif p1[x] == p2[y]:

            solution.append(p1[x])
            x += 1
            y += 1
        elif p1[x] > p2[y]:
            y += 1

    return solution


def union(p1, p2):
    """
    Method to compute the union of two postings lists.  Takes two
    postings lists as arguments and returns the union.
    """
    if p1[0] < 0 or p2[0] < 0:
        raise NotImplementedError('p1 OR NOT p2 is not supported')

    x, y = 0, 0
    solution = []
    while True:

        if x >= len(p1):
            solution += p2[y:]
            break

        elif y >= len(p2):
            solution += p1[x:]
            break

        if p1[x] < p2[y]:
            solution.append(p1[x])
            x += 1
        elif p1[x] == p2[y]:
            solution.append(p1[x])
            x += 1
            y += 1
        elif p1[x] > p2[y]:
            solution.append(p2[y])
            y += 1

    return solution


def intersect_multiple(args):
    """Uses intersect to intersect a list of postings list"""
    result = args[0]
    for element in args[1:]:
        result = intersect(result, element)
    return result


def union_multiple(args):
    """Uses union to unite a list of postings lists"""
    result = args[0]
    for element in args[1:]:
        result = union(result, element)
    return result

if __name__ == '__main__':
    the_index = ReverseIndex(glob('corpus/*.txt'))

    queries = ['Caesar', 'hello', 'Brutus AND Calpurnia',
               'Brutus OR Hamlet',
               '(Brutus AND Calpurnia) OR (Romeo AND Juliet)',
               'Brutus AND NOT Calpurnia',
               'NOT Calpurnia AND Brutus',
               'NOT Brutus',
               #'NOT Brutus AND NOT Calpurnia',
               #'NOT Brutus OR NOT Calpurnia',
               #'Brutus OR NOT Calpurnia'
            ]
    for query in queries:
        print(f'Documents matching {query}:')
        documents = the_index.execute_query(query)
        for doc in documents:
            print(doc)
        print()



