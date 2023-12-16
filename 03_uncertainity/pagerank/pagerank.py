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


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pages = list(corpus.keys())
    linked_pages = corpus[page]
    probabilities = dict()

    total_prob = 0
    for page in pages:
        prob = 0
        if page in linked_pages:
            prob += damping_factor*(1/len(linked_pages))

        prob += (1-damping_factor)*(1/len(pages))

        probabilities[page] = prob
        total_prob += prob
    
    return {x:y/total_prob for x,y in probabilities.items()}


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    estimation = {x:0 for x in pages}

    start = random.choice(pages)
    estimation[start] += 1/n

    for i in range(n-1):
        trans_mod = transition_model(corpus,start, damping_factor)
        
        sampled = random.choices(
            population= list(trans_mod.keys()),
            weights= list(trans_mod.values()),
            k = 1
        )

        estimation[sampled[0]] += 1/n
        start = sampled[0]
    
    return estimation




def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    for key,item in corpus.items():
        if len(item) == 0:
            corpus[key] = list(corpus.keys())
            
    pages = list(corpus.keys())
    prior_pr = {x:1/len(pages) for x in pages}

    correct_value = {x:0 for x in pages}

    while sum(correct_value.values()) != len(pages):
        page = random.choice(pages)
        prob = 0

        links_list = [link for link in pages if page in corpus[link]]
        prob += (1-damping_factor)/len(pages)
        for link in links_list:
            if len(corpus[link]) != 0:
                prob += damping_factor*(prior_pr[link]/len(corpus[link]))
            else:
                prob += damping_factor*(prior_pr[link]/len(pages))

        pr_prob = prior_pr[page]
        prior_pr[page] = prob

        sum_values = sum(prior_pr.values())
        prior_pr = {x:y/sum_values for x,y in prior_pr.items()}

        if abs(pr_prob - prior_pr[page]) <= 0.001:
            correct_value[page] = 1
        else:
            correct_value[page] = 0
        
        

    
    return prior_pr



        




if __name__ == "__main__":
    main()
