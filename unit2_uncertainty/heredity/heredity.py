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

    people_probs = {}

    people_gene_trait = {}
    
    # joint people's name, # of gene, and has_trait info into one dictionary
    # if 
    for one in people.keys():
        # get one's number of gene
        if one in one_gene:
            one_n_gene = 1
        elif one in two_genes:
            one_n_gene = 2
        else:
            one_n_gene = 0
            
        # if one has trait
        if one in have_trait:
            one_has_trait = True
        else:
            one_has_trait = False
        
        # update person's gene and trait dict
        people_gene_trait[one] = {"n_gene": one_n_gene, "has_trait": one_has_trait}


    # loop over people
    for content in people.values():

        #  Get person's name, number of gene and has_trait info from people_gene_trait
        name = content['name']
        n_gene = people_gene_trait[name]['n_gene']
        has_trait = people_gene_trait[name]['has_trait']
        mother = content['mother']
        father = content['father']

        # PARENTS (person has no info about mother or father)
        if mother == None or father == None:
            # calculate person's (parent) prob and update perople_probs
            people_probs[name] = PROBS["gene"][n_gene] * PROBS["trait"][n_gene][has_trait]
            continue

        # CHILDREN

        # get person's gene_prob and trait_prob
        # person has 1 gene
        if n_gene == 1:
            # person has 1 gene, there are two cases
            # CASE 1: from (mother, not father)
            m_prob1 = get_gene_prob(people_gene_trait[mother]['n_gene'], True)
            f_prob1 = get_gene_prob(people_gene_trait[father]['n_gene'], False)

            # CASE 2: from (not mother, father)
            m_prob2 = get_gene_prob(people_gene_trait[mother]['n_gene'], False)
            f_prob2 = get_gene_prob(people_gene_trait[father]['n_gene'], True)

            # calculate person's conditional prob
            person_gene_prob = m_prob1 * f_prob1 + m_prob2 * f_prob2

        # person has 2 gene
        elif n_gene == 2:
            # person has two genes: from both mother and father
            m_prob = get_gene_prob(people_gene_trait[mother]['n_gene'], True)
            f_prob = get_gene_prob(people_gene_trait[father]['n_gene'], True)

            person_gene_prob = m_prob * f_prob

        # person has no gene
        else:
            # person has no genes: neither from mother nor father
            m_prob = get_gene_prob(people_gene_trait[mother]['n_gene'], False)
            f_prob = get_gene_prob(people_gene_trait[father]['n_gene'], False)

            person_gene_prob = m_prob * f_prob

        # get person's trait prob by checking PROBS: "trait" / n_gene / has_trait
        person_trait_prob = PROBS['trait'][n_gene][has_trait]

        # calculate person's (child) probability and update people_probs
        people_probs[name] = person_gene_prob * person_trait_prob

    # calculate total conditional prob
    # init probs_product
    prods_product = 1
    
    for prob in people_probs.values():
        prods_product *= prob
    print(prods_product)
    return prods_product


def get_gene_prob(n_gene, give_gene):
    """
    return the probability of the child get/or not gene from this parent [float]

    n_gene [int]: parent has number of gene
    give_gene [bool]: parent give gene to child 
    """
    # give gene to child
    if give_gene:
        # no such gene, prob = P(mut)
        if n_gene == 0:
            prob = PROBS['mutation']
        # 2 such gene, prob = P(not mut)
        elif n_gene == 2:
            prob = 1 - PROBS['mutation']
        # 1 of such gene, prob = 0.5
        else:
            prob = 0.5
    # doesn't give gene to child
    else:
        if n_gene == 0:
            prob = 1 - PROBS['mutation']
        elif n_gene == 2:
            prob = PROBS['mutation']
        else:
            prob = 0.5
    return prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene: 
            probabilities[person]["gene"][1] = p
            if person in have_trait:
                probabilities[person]["trait"][True] = p
            else:
                probabilities[person]["trait"][False] = p
        elif person in two_genes:
            probabilities[person]["gene"][2] = p
            if person in have_trait:
                probabilities[person]["trait"][True] = p
            else:
                probabilities[person]["trait"][False] = p
        else:
            probabilities[person]["gene"][0] = p
            if person in have_trait:
                probabilities[person]["trait"][True] = p
            else:
                probabilities[person]["trait"][False] = p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # calculate normalize factor for gene and for trait
    for person in probabilities:
        gene_factor = sum([g for g in probabilities[person]["gene"].values()])
        trait_factor = sum([t for t in probabilities[person]["trait"].values()])

        # normalize gene
        for k, v in probabilities[person]["gene"].items():
            probabilities[person]["gene"][k] = v / gene_factor

        # normalize trait
        for k, v in probabilities[person]["trait"].items():
            probabilities[person]["trait"][k] = v / trait_factor


if __name__ == "__main__":
    main()
