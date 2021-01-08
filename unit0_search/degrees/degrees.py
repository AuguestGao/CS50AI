"""
Degree

AG
2021-01-07
"""

import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Todo
    # For this problem:
    #   state = person
    #   action = movie
    
    # Init start
    start = Node(state=source, parent=None, action=None)
    
    # Init frontier with type queue and add start node to froniter
    frontier = QueueFrontier()
    frontier.add(start)

    # Init explored_states, proventing searching in a loop
    explored_states = []

    while True:
        # If nonething left in frontier & goal has not  been found: no solution
        if frontier.empty():
            raise Exception("Impossiable")

        # Remove a node from frotier (by its type)
        node = frontier.remove()

        # Node is goal: reverce action and state to get them in order
        if node.state == target:
            # Init an empty path from soure to target, format [(movie_id, person_id)...]
            path = []

            # Back tracking to start state
            while node.parent is not None:
                # Append path
                path.append((node.action, node.state))
                # Update node to be parent node
                node = node.parent

            # Reverse path and return
            path.reverse()
            print (f"explored states number: {len(explored_states)}")
            return path
            
        # Node is not goal, add state into explored_states
        explored_states.append(node.state)

        # Get neighbors
        neighbors = neighbors_for_person(node.state)

        # Init frontier candidates
        candidates = {}

        # Put neighbors in dictionary state:action
        for action, state in neighbors:
            candidates[state] = action

        # If target is in dictionary.keys: skip all other states
        if target in candidates.keys():
            child = Node(state = target, parent = node, action = candidates[target])
            frontier.add(child)
        else: 
            # Add all candidates into frontier for searching 
            for state, action in candidates.items():
                
                # If node is neither in explored_states nor in the frontier queue: add to frontier
                if (state not in explored_states) and (not frontier.contains_state(state)):
                
                    child = Node(state = state, parent = node, action = action)
                    frontier.add(child)

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
