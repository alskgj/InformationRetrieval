# for stripping punctuation
# cf. https://stackoverflow.com/a/34294398
def remove_punctuation(s):
    import string
    trans = str.maketrans('', '', string.punctuation)
    return s.translate(trans)


def tokenize_document(doc):
    '''
    Simple tokenizer for a single document referred to by a file name.
    To keep it efficient we implement the tokenizer as a python generator.
    '''
    with open(doc, encoding='utf-8') as d:
        for line in d:
            words = line.strip().split()
            for w in words:
                yield remove_punctuation(w)
