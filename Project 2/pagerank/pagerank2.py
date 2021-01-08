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
    model = dict()

    # Get all possible pages in corpus
    possible_pages = corpus[page]
    
    # If the current page has no links out of the page, then damping factor = 0
    # Chance to go to any random page becomes 100%
    if len(possible_pages) == 0:
        damping_factor = 0.0
    
    # Add all pages to the probability, and calculate the probability for each page using the following formula
    # (1 - damping factor) / total number of pages + 
    # damping factor / total number of links in the page    
    for current_page, links in corpus.items():
        model[current_page] = (1 - damping_factor) / len(corpus)

        # To prevent divide by 0 error if there is no links, prevents adding to itself
        if damping_factor != 0.0 and current_page is not page:
            number_of_links = len(corpus[page])
            if page in corpus[page]:
                number_of_links -= 1
            if current_page in corpus[page]:
                model[current_page] += damping_factor / number_of_links

    # # Print Testing - Should print the number 1 as total probability
    # total_probability = 0
    # for each_page, probability in model.items():
    #     total_probability += probability
    # print(f"transition_model(): Total Probability for {page} is : {total_probability}")

    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Get all pages in corpus
    all_pages = []
    pageCount_dict = dict()     # Counts the number of time each page is visited

    # Initialise all pagerank count to 0
    for pages_name, linked_page in corpus.items():
        all_pages.append(pages_name)
        pageCount_dict[pages_name] = 0

    # Get a random initial page
    current_page = random.choice(all_pages)
    pageCount_dict[current_page] += 1

    # Sample n-1 times to random pages
    if (n - 1) >= 0: 
        for i in range(n - 1):
            current_page_probabilities = transition_model(corpus, current_page, damping_factor)
            possible_pages = []
            possible_pages_proability = []
            
            for page, score in current_page_probabilities.items():
                possible_pages.append(page)
                possible_pages_proability.append(score)
            
            # Sample based on probability
            current_page = random.choices(possible_pages, weights=possible_pages_proability, k=1)[0]
            pageCount_dict[current_page] += 1    
    
    # Get the distribution
    for page, count in pageCount_dict.items():
        pageCount_dict[page] = count / n

    # Print Testing
    total_probability = 0
    for page, count in pageCount_dict.items():
        total_probability += count

    # print(pageCount_dict)
    return pageCount_dict


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # PR(p) = ((1-d) / N) + d (sum of (pr(i) / num of links(i))
    # d is the damping factor
    # n is the total number of pages in the corpus
    # i is all pages that links to p
    # numlinks(i) is the number of links present on (i)
    
    ranking = dict()
    prevRank = dict()
    rank_check = True

    for page, links in corpus.items():
        prevRank[page] = 1 / len(corpus)

    while rank_check:
        # Stop repeating
        rank_check = False
        
        for page, score in prevRank.items():
            # Check if any references to current page
            reference_list = []  # Contains score / number of links
            
            # Calculate the first part of the formula
            ranking[page] = (1 - damping_factor) / len(corpus)

            # For all items, if the current page appear as a reference
            for reference, referencelink in corpus.items():
                if page in referencelink and page is not reference:
                    reference_list.append(prevRank[reference] / len(referencelink))
                elif len(referencelink) == 0:
                    reference_list.append(prevRank[reference] / len(corpus))
            
            # Calculate new score=
            ranking[page] += (damping_factor * sum(reference_list))
                
            # Check for >= 0.001 variance
            if abs(prevRank[page] - ranking[page]) >= 0.001:
                rank_check = True
        
        prevRank = ranking.copy()

    # print(f"{sum(ranking.values())}")
    
    return ranking


if __name__ == "__main__":
    main()
