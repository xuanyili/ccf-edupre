import spacy

nlp = spacy.load('zh_core_web_sm')

def compare_name(name1, name2):
    if name1 == [] or name2 == []:
        return 0.1
    doc1 = nlp(name1)
    doc2 = nlp(name2)
    return  doc1.similarity(doc2)