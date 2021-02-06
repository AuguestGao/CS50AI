import nltk
import sys
import re
import math
import os
from collections import Counter

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = {}
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), encoding="UTF-8") as f:
            files[filename] = f.read()

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    tokens = nltk.word_tokenize(document)
    stopwords = nltk.corpus.stopwords.words("english")
    #punctuations = string.punctuation
    words = [token.lower()
             for token in tokens if token.lower() not in stopwords and re.match(r"[a-zA-Z0-9]+", token)]

    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = {}
    total_docs = len(documents)

    # get all unique words
    all_words = []
    for words in documents.values():
        all_words += words
    uni_words = set(all_words)

    for word in uni_words:
        count = 0
        for words in documents.values():
            if word in words:
                count += 1
        idfs[word] = math.log(total_docs / count)

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idfs = []

    # loop over files
    for file, tokens in files.items():
        score = 0
        # loop over words in query
        for word in query:
            tf = tokens.count(word)
            # get idf for word or 0 if the word doesn't exist
            idf = idfs.get(word, 0)
            score += tf * idf
        tf_idfs.append((file, score))

    # sort according to score in descenting order
    sorted_tf_idfs = sorted(tf_idfs, key=lambda i: i[1], reverse=True)
    top_n_files = [i[0] for i in sorted_tf_idfs]

    return top_n_files[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    results = []
    for sentence, words in sentences.items():
        score = 0
        for word in query:
            if word in words:
                score += idfs.get(word, 0)
        results.append((sentence, score))

    score_results = sorted(results, key=lambda i: i[1], reverse=True)

    # extract all scores, and remember all ties
    all_scores = [score for sentence, score in score_results]
    counter = Counter(all_scores)
    tie_scores = [score for score, num in counter.items() if num > 1]

    # order top_sentence due to score, if there is a tie, order by tf
    top_sentences = []

    while score_results:

        sentence, score = score_results.pop(0)

        if sentence in top_sentences:
            continue

        if score not in tie_scores:
            top_sentences.append(sentence)
            continue
        else:
            tie_sentences=[]
            tie_sentences.append(sentence)
            tie_sentences += [sent for sent,
                             sc in score_results if sc == score]
            sorted_sentences = sort_tie(tie_sentences, sentences, score, query)
            top_sentences += sorted_sentences

    return top_sentences[:n]


def sort_tie(tie_sentences, sentences, score, query):

    tfs = []
    for sentence in tie_sentences:
        len_sentence = len(sentences[sentence])
        counter = 0
        for word in set(sentences[sentence]):
            if word in query:
                counter += 1

        tfs.append((sentence, counter / len_sentence))

    sorted_tfs = sorted(tfs, key=lambda i: i[1], reverse=True)

    sorted_sentences = [i[0] for i in sorted_tfs]
    return sorted_sentences


if __name__ == "__main__":
    main()
