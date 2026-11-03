# Likely interview questions and model answers

Written in the first person so you can adapt them. Keep real answers shorter than these. Mark the ones you want to practice out loud. Questions about the project itself are at the end, and the awkward ones are in `DEMO_SCRIPT.md`, section 6.

## RDF and linked data

**What is RDF, and how is it different from a property graph like Neo4j?**
RDF stores facts as triples of subject, predicate and object. Every node and relation has a global name, a URI, so data from different sources can be merged without a shared database. In a property graph like Neo4j, identifiers are local to one database, and relationships can carry properties. In RDF, to say something about a relationship you model it as a thing of its own. Neo4j is strong for traversal inside one system, and RDF is strong for publishing and linking across systems.

**Why do linked data identifiers have to be URIs?**
Because they must be globally unique and, ideally, resolvable. Two organizations can then talk about the same thing and link their data without agreeing on a central key.

**What are the linked data principles?**
Name things with URIs, use HTTP URIs so they can be looked up, return useful RDF when they are looked up, and link to other URIs.

**What is the limit of your URIs?**
They live on GitHub Pages, which is static. It cannot do content negotiation, so the URIs are stable names but do not return RDF on their own. I publish the files in `data/dist` and wrote the limit down in the modeling decisions.

**Which serializations do you publish and why?**
Turtle as the source of truth, because it is readable and diffs well in git. JSON-LD and RDF/XML are generated from it, and a test fails if they ever disagree with the Turtle.

## SKOS and vocabularies

**What is SKOS for?**
For vocabularies and thesauri: concepts with preferred and alternative labels in several languages, definitions, and broader, narrower and related links. It is the standard behind EuroVoc.

**What is the difference between prefLabel and altLabel?**
`prefLabel` is the single preferred name in a language. `altLabel` holds synonyms, abbreviations and spelling variants. A concept may have only one preferred label per language, and I enforce that with SHACL.

**Is skos:broader the same as rdfs:subClassOf?**
No. Broader means "belongs under" for navigation. Subclass means every member of one class is a member of the other. *Right to erasure* is under *Data subject*, but a right is not a kind of person.

**How do you handle translations?**
Every concept has labels in English, French and German. Ten take their labels from EuroVoc. The rest I wrote and flagged with a `pendingReview` property. The app shows a chip, and a generated file lists every concept to check. I am not a native speaker of either language, so I would not call them verified.

**How do you align with EuroVoc?**
With SKOS mapping properties: `exactMatch` for the same meaning, `closeMatch` for similar, `broadMatch` where the EuroVoc concept is broader. I looked up all 19 identifiers in the official data and chose the link types myself, so an expert should review them.

**Why not reuse EuroVoc directly?**
My slice is narrow, and I wanted definitions written for non-experts and a structure around regulation topics. Mapping links keep it interoperable without pretending to be EuroVoc.

**How would you maintain a vocabulary over time?**
Stable identifiers that never change, labels that can, a clear workflow for adding a concept with automatic checks (the how-to guide), versioning, a review process for translations, and deprecating concepts with a pointer to the replacement and not deleting them.

## OWL and reasoning

**What does your ontology contain?**
Classes for legal acts, regulations, directives, implementing regulations, authorities and obligations. Properties for amends, repeals, is based on, has topic, regulates, provides for, imposes obligation, has ELI and has CELEX. Axioms for domain and range, inverse, asymmetric and functional properties, a sub-property, and disjoint classes.

**Show me a piece of inference.**
The data says the GDPR is a Regulation. The ontology says every Regulation is a LegalAct, so the reasoner adds that the GDPR is a LegalAct. Another: the data says the GDPR repeals the 1995 directive, and `repeals` is the inverse of `repealedBy`, so the reverse statement is added.

**Why did you make regulates a sub-property of hasTopic?**
It models that the main subject of an act is also one of its topics, and it shows the benefit of sub-property reasoning. It also explains why my query 11 needs both properties when no reasoner is running.

**What is the open world assumption?**
Missing information is unknown, not false. So an OWL model cannot say a property is required.

**When do you use SKOS and when OWL?**
SKOS for terms and their meaning, with translations and a hierarchy of "belongs under". OWL for kinds of things and their relations, where logic and inference matter. My project uses both and joins them with one property, `hasTopic`.

**Did you use a reasoner in production?**
No. I used owlrl, a small OWL RL reasoner, to demonstrate inference and contradiction detection. The queries and the shapes do not depend on it.

## SPARQL

**Explain a property path.**
A property path follows a link several times. `skos:broader+` means one or more steps, so it finds all descendants of a concept. `*` also includes the starting concept. `|` accepts alternatives.

**How do you find data that is missing?**
`FILTER NOT EXISTS`. My query 08 finds concepts without a French or German label, and returns no rows today.

**Difference between OPTIONAL and FILTER NOT EXISTS?**
OPTIONAL keeps the row and leaves a variable empty if there is no match. `FILTER NOT EXISTS` keeps the row only if there is no match.

**How do you count per group?**
`GROUP BY` with `COUNT`. Query 07 counts descendants per top concept, and a test checks that the counts plus the six top concepts equal all 68 concepts.

**What is CONSTRUCT?**
It builds a new graph from the matches and not a table. Query 15 builds a small graph that links acts to topics.

**How do you query across the thesaurus and the dataset?**
They are in the same graph, and `lab:hasTopic` links them. Query 11 follows `skos:broader*` from a topic and joins to the acts.

**How do you let users run SPARQL safely?**
The playground parses the text and refuses anything but SELECT, ASK, CONSTRUCT and DESCRIBE. It refuses `SERVICE`, stops after 10 seconds and returns at most 2,000 rows.

## SHACL and data quality

**What is SHACL?**
A standard for describing what valid RDF looks like and checking data against it.

**SHACL versus OWL?**
OWL infers facts and works under the open world assumption. SHACL validates, treating missing data as an error. Use OWL for what things mean and SHACL for what the data must contain.

**What do your shapes check?**
For concepts: an English label, a definition, one preferred label per language, no label shared by two concepts in a language, and broader and narrower links that mirror each other. For acts: one CELEX number in the right pattern and consistent with the class, an English title, a typed date, an ELI, and topics that are real concepts. For datasets: title, description, publisher, license, language, theme and a distribution.

**How do you know the shapes work?**
Negative tests. Nine small files are broken on purpose, and the tests require each one to fail with the expected message, except the translation example, which must only give warnings.

**What is severity?**
A violation fails validation. A warning is reported but does not fail. Missing French or German labels are warnings.

**How would you run this in a pipeline?**
`python -m semlab validate` exits with a non-zero code on a violation, and the CI workflow runs it with the tests and the lint on every push.

## Open data, DCAT, standards

**What is DCAT, and what is DCAT-AP?**
DCAT is the W3C vocabulary for describing datasets in catalogs: catalog, dataset, distribution. DCAT-AP is the European application profile, used by data.europa.eu and national portals, which adds mandatory properties and controlled vocabularies.

**Is your catalog DCAT-AP compliant?**
It is DCAT-AP style. It uses the same structure and the EU code lists for language, theme, file type, license and frequency, but I did not run an official validation, so I do not claim conformance.

**What are the FAIR principles, and how does your project meet them?**
Findable, Accessible, Interoperable, Reusable. Persistent URIs and rich metadata, an open repository, standard vocabularies with links to EuroVoc and ELI, and clear licenses and sources. What is missing: registration in a portal and content negotiation.

**What licenses did you choose?**
MIT for code and CC BY 4.0 for data. EuroVoc labels keep EuroVoc's own terms, which I documented.

**What are CELEX and ELI?**
CELEX is the identifier EUR-Lex gives to an act, built from sector, year, type and number. ELI is the European Legislation Identifier, a standard, permanent web address for legislation.

**How would you publish reference data for others to reuse?**
Stable URIs, SKOS concept schemes with versions, downloads in several serializations, a DCAT description with a license and a contact point, and a way to follow changes.

## About the project

**Walk me through the architecture.**
Hand-edited Turtle files are the source of truth. A small Python package loads them into an rdflib graph, validates them with SHACL, optionally reasons with OWL RL, and runs the queries. A Streamlit app shows it all. JSON-LD and RDF/XML are generated, and CI runs lint, tests and validation.

**How do you test it?**
Data integrity tests, SHACL tests with positive and negative cases, a test for each of the 15 queries with results worked out from the design, reasoning tests, safety tests for the playground, mocked network tests for the Cellar module, and app tests.

**What was the hardest part?**
Making the quality checks both useful and fast. A first version of the unique label rule took about ten seconds, because it compared every label with every other. I rewrote it as an indexed lookup on the same value and language, and validation went from about ten seconds to under one.

**What would you do next?**
Review the translations with native speakers, cite articles and not only acts, publish with content negotiation, add a Fuseki endpoint, and register the catalog in a portal.

**How is this relevant to this role?**
The role covers ontologies, SKOS vocabularies, linked open data, SPARQL, standards, reference data, open data publishing and training. The project touches each: SKOS, OWL, SPARQL, DCAT, alignment with EuroVoc and ELI, and the guide and workshop for non-technical users.

**How would you explain this to a non-technical colleague?**
"A shared list of terms with translations, a set of facts about laws that point to those terms, and automatic checks so that mistakes are caught. You can click through it and ask it questions without writing code."

## About you (adapt)

**Why semantic technologies, coming from Neo4j and data governance?**
Governance is about shared meaning and quality, and semantic standards put that in a form that is reusable and checkable across organizations. My graph database experience gave me the intuition, and this project is how I moved from that to the standards.

**What do you not know yet?**
Be direct: production triple stores, formal DCAT-AP validation, and EuroVoc maintenance workflows. Say how you would learn each.
