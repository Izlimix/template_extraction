#!/usr/bin/env python3
from bs4 import BeautifulSoup, NavigableString, Tag

# TODO:
# - tag equality/similarity
# - traversing trees that have unequal numbers of children / the order doesn't match exactly
# -- Can pair by looking at the next child of the same type. Try for multiple start points, pick best?
# - Extracting the relevant nodes when a template is found.
# - Content extraction: Given a template, keep only the non-template nodes (maybe labelling somehow to keep some structure) 
# - Template-tagging: Use HTML classes instead of python attributes? (might clash with existing, plus it'd be printed)
# - Note: Limitations of static page analysis vs the Firefox extension. This script can't run any js that might edit the page, but the extension can be called after js is executed.

def main(f1, f2):
    print(f"Opening {f1} and {f2}")
    # Take 2 filenames and parse each as a DOM tree
    with open(f1, encoding="utf-8") as f:
        t1 = BeautifulSoup(f.read(), "html.parser")
    with open(f2, encoding="utf-8") as f:
        t2 = BeautifulSoup(f.read(), "html.parser")

    # Then compare the 2 trees and extract the common parts to create a template
    print(f"Same according to bs4?: {t1 == t2}")
    __print_separator()
    #show_equal_descendants(t1, t2)
    tag_equal_descendants(t1, t2)
    print("Done tagging. Showing:")
    __print_separator()
    show_tagged(t1, False)
    pass

def __print_separator():
    print("-"*100)

def tags_equal(t1, t2):
    return t1.name == t2.name # Note: BeautifulSoup tag equality (==) is already recursive all the way down. But we just want to see if this part is probably equal
    # equal/similar tags
    # 1. Should have the same t.name (e.g. span, p, etc.)
    # 2. If they have ids, they should be the same
    # 3. If they have classes, they should match up
    # 4. The number of children should match up
    # 4a. could also look at the types of the children, but that's prob overkill
    # Note: ETDM used a probability for each, then summed them and compared against a threshold.

def show_equal_descendants(t1, t2):
    # todo: bs4.BeautifulSoup is an instance of bs4.Tag. Can use tags_equal if both tag instances, else == ?
    if isinstance(t1, NavigableString) or isinstance(t2, NavigableString):
        if t1 == t2:
            s = t1.strip()[:100]
            if s:
                print(f"Found string: {s}")
    else:
        if tags_equal(t1, t2):
            print(f"Found tag: {t1.name}")
            for (c1, c2) in zip(t1.children, t2.children):
                show_equal_descendants(c1, c2)

def tag_equal_descendants(t1, t2):
    if isinstance(t1, Tag) and isinstance(t2, Tag):
        if tags_equal(t1, t2):
            t1.__is_template = True
            t2.__is_template = True
            for (c1, c2) in zip(t1.children, t2.children):
                tag_equal_descendants(c1, c2)
    else:
        if t1 == t2:
            t1.__is_template = True
            t2.__is_template = True

def show_tagged(t, template_mode=True):
    """
    if isinstance(t, Tag):
        if t.__is_template:
            print(t)
            for c in t.children:
                show_tagged(c, template_mode=template_mode)
    else:
        if t.__is_template:
            print(t)
    """
    print(t.find_all(__is_template_tagged, template_mode))

def __foo(t1, t2):
    # Given two aligned nodes from different pages, try to align their children
    # Basic: Same tag types in order
    pairs = dict()
    c2 = t2.find(recursive=False) # TODO: fix! This finds the first tag, and not the first child (e.g. string)! Might be the same for the other bs4 find()s
    for c1 in t1.children:
        # Need to make sure c2 isn't None after it moves
        if c2 is None: break
        if isinstance(c1, Tag):
            if isinstance(c2, Tag) and tags_equal(c1, c2):
                pairs[c1] = c2
                c2 = c2.find_next_sibling()
            else:
                for candidate in c2.find_next_siblings(c1.name):
                    if tags_equal(c1, candidate):
                        pairs[c1] = candidate
                        c2 = candidate.find_next_sibling()
                        break
        else:
            # c1 is some sort of string
            if c1 == c2:
                pairs[c1] = c2
                c2 = c2.find_next_sibling()
            else:
                for candidate in c2.find_next_siblings():
                    if c1 == c2:
                        pairs[c1] = c2
                        c2 = c2.find_next_sibling()
                        break
    return pairs


def __is_template_tagged(n, template_mode=True):
    return getattr(n, "__is_template", False) == template_mode

def __weighted_sum(weights, ns):
    return sum(w * n for (w, n) in zip(weights, ns))

def __weighted_avg(weights, ns):
    return __weighted_sum(weights, ns) / len(ns)

# Command-line script execution
# (Can use the python arg parsing module sys.argv or argparse)
if __name__ == "__main__":
    import sys
    """
    print(f"Received {len(sys.argv)-1} non-standard args:")
    for i in range(1, len(sys.argv)):
        print(i, sys.argv[i])
    """
    main(sys.argv[1], sys.argv[2])