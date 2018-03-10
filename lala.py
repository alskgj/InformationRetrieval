from queryparser import process_ast, parse_query


def parse(flat):
    if isinstance(flat, str):
        return flat
    op = flat.op
    print(op)
    # we are at a leaf

    args = [parse(e) for e in flat.args]
    if op == 'AND':
        return intersect(args)
    elif op == 'OR':
        return union(args)


def intersect(args):
    print('anding the list', args)
    return 'intersected'


def union(args):
    print('oring the list', args)
    return 'ored'


query = '(Brutus AND Calpurnia) OR (Romeo AND Juliet)'
query = 'Brutus AND NOT Calpurnia'
ast = parse_query(query)
flat = process_ast(ast)
print(flat)

parse(flat)