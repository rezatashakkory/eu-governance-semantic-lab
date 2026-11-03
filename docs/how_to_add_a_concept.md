# How to add a concept

This guide adds one new concept to the thesaurus. It takes about ten minutes. You need a text editor and the project installed (see the README quickstart).

## Before you start: is it really a new concept?

1. Search for it in the app (Vocabulary Browser, search box) in English, French and German.
2. If a concept already means the same thing, add the new wording as an alternative label instead (step 5).
3. Decide where it belongs. Find the concept that is one step broader. Example: *Data breach notification* belongs under *Personal data breach*.

## Step 1: choose the identifier

The identifier is the last part of the URI. Use lowercase English words joined by hyphens: `data-breach-notification`. The identifier never changes, even if you later reword the label.

## Step 2: write the concept

Open `data/vocabulary/eu-data-governance.ttl`. Copy an existing concept in the right section and change it. A complete example:

```turtle
cpt:data-breach-notification a skos:Concept ;
    skos:inScheme sch:eu-data-governance ;
    skos:prefLabel "Data breach notification"@en,
                   "notification de violation de données"@fr,
                   "Meldung einer Datenschutzverletzung"@de ;
    skos:definition "The duty to tell the supervisory authority, and sometimes the affected people, about a personal data breach."@en ;
    skos:broader cpt:personal-data-breach ;
    dct:source act:32016R0679 ;
    lab:pendingReview "fr", "de" .
```

Rules the checks enforce:
- One English `skos:prefLabel`, and no more than one preferred label per language.
- A `skos:definition`.
- A `skos:broader` link, unless the concept is a top concept.
- The preferred label must not be used by another concept in the same language.

Always add `lab:pendingReview "fr", "de"` unless a native speaker has checked the translations.

## Step 3: tell the parent about its child

In the parent concept (`cpt:personal-data-breach`), add the new concept to `skos:narrower`:

```turtle
skos:narrower cpt:data-breach-notification ;
```

The checks fail if a `narrower` link has no matching `broader` link, and the other way around.

## Step 4: optional links

- `skos:related cpt:other-concept` links two related concepts. Add it on **both** concepts. A test checks that related links are symmetric.
- `skos:exactMatch`, `skos:closeMatch` or `skos:broadMatch` with a EuroVoc URI. Only add a link you have verified. Look the concept up on the EuroVoc page of the EU Vocabularies site, and read the decisions in `docs/modeling_decisions.md` (D6) to pick the right link type.
- `dct:source act:CELEX` names the act the definition is based on. The act must exist in `data/dataset/legal-acts.ttl`.

## Step 5: alternative labels

Synonyms, abbreviations and spelling variants go in `skos:altLabel`:

```turtle
skos:altLabel "DBN"@en ;
```

## Step 6: check your work

```bash
python -m semlab validate
python -m pytest tests/test_data.py tests/test_shacl.py
```

If validation fails, the message names the concept and the problem. Fix it and run again.

Two tests count things on purpose (68 concepts, 6 top concepts, 58 pending reviews). A new concept changes those numbers. Update the expected values in `tests/test_data.py`, `tests/test_queries.py` (queries 02, 05 and 07) and `tests/test_helpers.py`, and the numbers in the README. This is deliberate: a number that changes without anyone noticing is a data quality problem.

## Step 7: regenerate the other files

```bash
python -m semlab build          # JSON-LD and RDF/XML
python -m semlab translations   # the review list
python -m pytest
```

Commit with a message such as `feat(vocabulary): add data breach notification`.
