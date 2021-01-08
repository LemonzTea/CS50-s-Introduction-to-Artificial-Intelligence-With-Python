import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.
    
    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    
    def calculate_parent_probability(gene_count, inherit_gene=True):
        """ Parameters 
            `has_genee` - Accepts true / false value if parents should or should not have the gene
            `inherit_gene` - Accepts true / false value if the child inherit the gene

            Returns the probability of a child inheriting or not inheriting a gene
        """
        if gene_count == 0:
            if inherit_gene:
                return PROBS["mutation"]
            else:
                return 1 - PROBS["mutation"]
        
        elif gene_count == 1:
            return 0.5
        
        else:
            if inherit_gene:
                return 1 - PROBS["mutation"]
            else:
                return PROBS["mutation"]
    
    probability_records = []

    for person in people: 
        # Declare information for person
        number_of_genes = count_gene(person, one_gene, two_genes)                # Number of gene for an individual
        individual_probability = 0                                               # Record probability of person having trait or no traint

        # if the person has no parents
        mother_name = people[person]["mother"]
        father_name = people[person]["father"]

        if mother_name is None and father_name is None:
            # Probability of getting genes naturally
            individual_probability = PROBS["gene"][number_of_genes]

        else:
            mother_gene = count_gene(mother_name, one_gene, two_genes)
            father_gene = count_gene(father_name, one_gene, two_genes)

            if number_of_genes == 0:
                # Do not inherit from both parents
                individual_probability = calculate_parent_probability(mother_gene, inherit_gene=False) * calculate_parent_probability(father_gene, inherit_gene=False)
            
            elif number_of_genes == 1:
                # Inherit from mother = true, father = false + 
                # Inherit from mother = false, father = true
                individual_probability = calculate_parent_probability(mother_gene) * calculate_parent_probability(father_gene, inherit_gene=False)
                individual_probability += calculate_parent_probability(mother_gene, inherit_gene=False) * calculate_parent_probability(father_gene)
            
            elif number_of_genes == 2:
                # Inherit from mother = true, father = true
                individual_probability = calculate_parent_probability(mother_gene) * calculate_parent_probability(father_gene)
            
        # Calculate change to have / dont have trait with given genes
        individual_probability *= PROBS['trait'][number_of_genes][person in have_trait]
        probability_records.append(individual_probability)
    
    # Multiply all probability together
    probability_joint = 1
    for probability in probability_records:
        probability_joint *= probability
    
    return probability_joint


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    # Update each's person probability of having 'x' number of genes
    # Update each's person probability of having trait
    for person in probabilities:
        gene_count = 0
        if person in one_gene:
            gene_count = 1
        elif person in two_genes:
            gene_count = 2

        probabilities[person]["gene"][gene_count] += p
        probabilities[person]["trait"][person in have_trait] += p



def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for person, individual_probability in probabilities.items():
        # Calculate the total value of gene and trait
        total_probability_gene = sum(individual_probability["gene"].values())
        total_probability_trait = sum(individual_probability["trait"].values())

        # Normalise each values for gene
        for count, score in individual_probability["gene"].items():
            individual_probability["gene"][count] = 1 / total_probability_gene * score

        # Normalise each values for trait
        for count, score in individual_probability["trait"].items():
            individual_probability["trait"][count] = 1 / total_probability_trait * score  


def count_gene(person, one_gene, two_genes):
    """ Counts the number of genes for a person
        `one_gene` takes a set of people who has 1 gene
        `two_genes` takes a set of people who has 2 gene
    """

    if person in one_gene:
        return 1
    elif person in two_genes:
        return 2
    else:
        return 0


if __name__ == "__main__":
    main()
