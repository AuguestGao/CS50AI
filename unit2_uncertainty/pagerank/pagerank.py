import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages

def get_pages(corpus):
    """
    return all pages in the corpus, and number of the pages
    """
    all_pages = set()
    for p in corpus.keys():
        all_pages.add(p)
    return (all_pages, len(all_pages))


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    
    # Init returning probablities: probs
    probs = {}

    # get all pages and number of pages in corpus
    all_pages, N = get_pages(corpus)

    # retrive all outbound links in the current page, and record the number
    page_links = corpus[page]
    n_page_links = len(page_links)
    
    # the page has no outgoing links, return equal probablities for all pages
    if not n_page_links:
        prob = 1 / N
        for p in all_pages:
            probs[p] = prob
        return probs

    # otherwise, the page has outgoing link(s)
    for p in all_pages:
        # page is linked by the current page
        if p in page_links:
            prob = (1 - damping_factor) / N + damping_factor / n_page_links
            probs[p] = prob
        else:
            prob = (1 - damping_factor) / N
            probs[p] = prob
    return probs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # get pages and number of pages in corpus
    all_pages, N = get_pages(corpus)

    # Init 0 click for each page
    clicks = {}
    for page in all_pages:
        clicks[page] = 0

    # randomly sleect a page to start
    start = random.choice(list(all_pages))
    # update click by 1 for start page
    clicks[start] += 1

    # n sampling
    for i in range(n):
        probs = transition_model(corpus, start, damping_factor)
        
        # random number
        rn = random.random()

        # go to page by checking rn and which interval it falls into
        sum = 0
        for page, prob in probs.items():
            sum += prob
            if rn <= sum:
                # update next page (start) to page and its rank by 1
                start = page
                clicks[start] += 1
                break # break loop
    
    # clicks / sample size = probability 
    ranks = {page:click / n for page, click in clicks.items()}
    return ranks

def get_is(corpus, current):
    """
    return a list of previous PR and num of links to page (PR(i), NumLinks(i)) for page

    Detail: https://cs50.harvard.edu/ai/2020/projects/2/pagerank/#:~:text=s.%20Each%20key%20should%20be%20mapped%20to%20a%20value%20representing%20that%20page’s%20PageRank.%20The%20values%20in%20this%20dictionary%20should%20sum%20to%201.
    """

    i_s = {}

    # list all key, value pairs in corpus
    for page, links in corpus.items():
        # if current page is in the links, meaning can bring surfers from page to current
        if current in links:
            # append page: number of links in the page into pre_page_links
            i_s[page] = len(links)
    
    return i_s

def get_sum(corpus, current, ranks):
    """
    Return the sum of i-terms for page with current ranks
    """

    # init
    i_sum = 0

    # get page name and numlinks of the page that can bring surfers to current page
    i_s = get_is(corpus, current)

    for name, numlinks in i_s.items():
        i_sum += ranks[name] / numlinks

    return i_sum        


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    all_pages, N = get_pages(corpus)

    # Init ranks to be 1 / N
    ranks = {}
    for page in all_pages:
        ranks[page] = 1 / N
    
    # iterate until delta <= 0.001
    while True:
        # Init new_ranks to store ranks from new iteration
        new_ranks = {}

        # calculate ranks according to formular for each page
        for p, r in ranks.items():
            # calculate i-term rank for this page
            i_sum = get_sum(corpus, p, ranks)
            new_ranks[p] = (1 - damping_factor) / N + damping_factor * i_sum

        # Init max delta to 0 for this iteration
        max_delta = 0

        # compare ranks between ranks and new_ranks, calculate delta for each page
        for page in all_pages:
            delta = abs(new_ranks[page] - ranks[page])
            # update delta to be max for each iteration
            if max_delta < delta:
                max_delta = delta
        
        ranks = new_ranks

        # check if the requirement is met
        if max_delta < 0.001:
            return ranks


if __name__ == "__main__":
    main()
