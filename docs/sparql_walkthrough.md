# SPARQL walkthrough

The 15 queries live in `queries/`. Each file starts with a header (title, level, purpose, expected result, concepts used) and has comments inside the query. Run any of them with `python -m semlab queries 7` or in the app. Every query has a test in `tests/test_queries.py` that checks the documented result.

## How to read a SPARQL query

SPARQL looks like SQL, but you describe a *pattern of triples* instead of tables.

```sparql
SELECT ?concept ?label          # what columns you want back
WHERE {                         # the pattern to match
  ?concept skos:prefLabel ?label .   # a triple pattern: any subject, this property, any value
}
```

- A word starting with `?` is a variable. The engine finds every way to fill the variables so that all patterns match.
- `skos:prefLabel` is a prefix plus a name. The `PREFIX` lines at the top say what `skos:` stands for.
- `a` means `rdf:type`. `;` repeats the subject. `.` ends a pattern.

## All queries at a glance

| No. | Level | Purpose | Main technique |
| --- | --- | --- | --- |
| 01 | easy | The six top concepts | Triple pattern, language FILTER |
| 02 | easy | Labels in three languages side by side | OPTIONAL |
| 03 | easy | Keyword search | FILTER regex |
| 04 | easy | Direct narrower concepts | One step of `skos:broader` |
| 05 | intermediate | All descendants | Property path `+` |
| 06 | intermediate | Ancestors of a concept | Property path `+` in reverse |
| 07 | intermediate | Concepts per top concept | GROUP BY, COUNT |
| 08 | intermediate | **Data quality**: missing translations | FILTER NOT EXISTS |
| 09 | intermediate | Links to EuroVoc | VALUES, BIND, REPLACE |
| 10 | easy | Overview of the acts | FILTER IN, ORDER BY |
| 11 | advanced | Acts about a topic and its narrower topics | Alternative path `\|`, path `*`, join of two datasets |
| 12 | intermediate | Amends, repeals, is based on | UNION |
| 13 | intermediate | Acts per type | GROUP BY, STRAFTER |
| 14 | intermediate | **Data quality**: any concept without a definition | ASK |
| 15 | advanced | A graph of acts and topics | CONSTRUCT |

## Line by line: query 04, direct narrower concepts

**Purpose.** List the concepts directly below *Data protection*.

```sparql
SELECT ?concept ?label
WHERE {
  ?concept skos:broader cpt:data-protection ;
           skos:prefLabel ?label .
  FILTER (lang(?label) = "en")
}
ORDER BY ?label
```

1. `SELECT ?concept ?label` asks for two columns.
2. `?concept skos:broader cpt:data-protection` finds every concept whose broader concept is *Data protection*. The subject is the variable, the object is fixed.
3. `; skos:prefLabel ?label` reuses the same subject and also asks for its preferred label. Each concept has three labels, so at this point there are three rows per concept.
4. `FILTER (lang(?label) = "en")` keeps the English row only.
5. `ORDER BY ?label` sorts alphabetically.

**Result.** 11 rows: Anonymization, Consent, Data controller, and so on.

## Line by line: query 05, all descendants

```sparql
?concept skos:broader+ cpt:data-protection ;
         skos:prefLabel ?label .
```

The only change from query 04 is the `+`. It means "one or more steps of `skos:broader`". The engine follows the link repeatedly, so *Special categories of personal data* is found through *Personal data*. SKOS does not make `broader` transitive by itself, so the property path does that work. With `*` (zero or more steps) the concept itself would also be included.

**Result.** 14 rows: the 11 from query 04 plus *Special categories of personal data*, *Data portability* and *Right to erasure*.

## Line by line: query 07, concepts per top concept

```sparql
SELECT ?topLabel (COUNT(DISTINCT ?concept) AS ?descendants)
WHERE {
  sch:eu-data-governance skos:hasTopConcept ?top .
  ?top skos:prefLabel ?topLabel .
  FILTER (lang(?topLabel) = "en")
  ?concept skos:broader+ ?top .
}
GROUP BY ?topLabel
ORDER BY DESC(?descendants) ?topLabel
```

1. The first pattern finds the six top concepts of the scheme.
2. The next two lines get their English labels.
3. `?concept skos:broader+ ?top` finds every descendant of each top concept.
4. `GROUP BY ?topLabel` makes one row per top concept. `COUNT(DISTINCT ?concept)` counts descendants in each group. `DISTINCT` guards against counting a concept twice if it could be reached by two paths.
5. `ORDER BY DESC(?descendants)` puts the biggest group first.

**Result.** Data protection 14, Data quality and metadata 12, AI governance 11, Digital resilience 9, Data governance 8, Open data and reuse 8. Together with the six top concepts that makes 68, the total number of concepts. A test checks this sum.

## Line by line: query 08, missing translations (data quality)

```sparql
SELECT ?concept ?enLabel ?missingLanguage
WHERE {
  ?concept a skos:Concept ;
           skos:prefLabel ?enLabel .
  FILTER (lang(?enLabel) = "en")
  VALUES ?missingLanguage { "fr" "de" }
  FILTER NOT EXISTS {
    ?concept skos:prefLabel ?other .
    FILTER (lang(?other) = ?missingLanguage)
  }
}
```

1. Take every concept with its English label.
2. `VALUES ?missingLanguage { "fr" "de" }` creates two copies of each row, one for each language to check.
3. `FILTER NOT EXISTS { ... }` keeps a row only if **no** preferred label exists in that language.

**Result.** Zero rows on the published data, which is the good result. A test adds a concept with only an English label and expects two rows back, one for each missing language.

## Line by line: query 11, acts about a topic and its narrower topics

```sparql
SELECT DISTINCT ?act ?shortName ?celex
WHERE {
  ?act (lab:hasTopic|lab:regulates) ?topic ;
       dct:alternative ?shortName ;
       lab:hasCELEX ?celex .
  ?topic skos:broader* cpt:data-protection .
}
ORDER BY ?celex
```

1. `(lab:hasTopic|lab:regulates)` is a path that accepts either property. The ontology says `regulates` is a sub-property of `hasTopic`, but plain SPARQL does not reason, so we ask for both.
2. The next two lines read the short name and CELEX number of the act.
3. `?topic skos:broader* cpt:data-protection` keeps topics that are *Data protection* itself or any concept below it. The `*` makes the starting concept count.
4. `DISTINCT` removes duplicates, because the GDPR has many matching topics.

This is the **join of two datasets**: acts come from the dataset, the hierarchy comes from the thesaurus, and `lab:hasTopic` is the link between them.

**Result.** 6 acts: GDPR, the 1995 Data Protection Directive, the EU institutions data protection regulation, ePrivacy, the Law Enforcement Directive and the European Health Data Space Regulation.

## Line by line: query 12, amends, repeals, is based on

```sparql
{ ?from lab:amends ?to . BIND ("amends" AS ?relation) }
UNION
{ ?from lab:repeals ?to . BIND ("repeals" AS ?relation) }
UNION
{ ?from lab:isBasedOn ?to . BIND ("is based on" AS ?relation) }
?from lab:hasCELEX ?fromCelex .
?to   lab:hasCELEX ?toCelex .
```

1. `UNION` combines the results of three alternative patterns, one per relation.
2. `BIND (... AS ?relation)` adds a column with a fixed word, so the reader can tell the three kinds apart.
3. The last two lines turn the two acts into CELEX numbers.

**Result.** 6 rows. For example `32022L2555 amends 32014R0910` says that the NIS2 Directive amends the eIDAS Regulation. These relations were taken from Cellar.

## Your turn: three queries to write yourself

Try each one before opening the answer notes. Use the playground.

1. **Which acts regulate Cybersecurity?** Hint: query 10 plus the property `lab:regulates`.
2. **Which concepts have an alternative label?** Hint: `skos:altLabel`, and `DISTINCT` if you only want the concept.
3. **Which concepts are linked to EuroVoc with `skos:exactMatch` and have a source act?** Hint: two triple patterns about the same `?concept`.

Answer notes:
1. `?act lab:regulates cpt:cybersecurity ; dct:alternative ?name .` Result: NIS2 Directive and Cyber Resilience Act.
2. `SELECT DISTINCT ?concept WHERE { ?concept skos:altLabel ?alt }`.
3. `?concept skos:exactMatch ?ev ; dct:source ?source .` Result: concepts with an exact match and a source act, such as *Data protection* and *Personal data*.
