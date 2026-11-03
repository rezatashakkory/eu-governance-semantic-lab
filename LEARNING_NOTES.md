# Learning notes

Short study notes, one section per phase. Read `STUDY_GUIDE.md` for the full explanations, and use this file for review. Under each phase: what was built and why, five key ideas, one thing to try, and two questions to answer aloud.

## Phase 0. Setup and RDF basics

**Built.** A Python package, tests, lint, pre-commit and CI, and the folder layout.
**Why.** Every later phase can be tested and committed safely.

**Five ideas.**
1. A triple is subject, predicate, object. A graph is a set of triples.
2. A URI is a global name for a thing, not necessarily a web page.
3. A literal is a plain value and can carry a language tag such as `@fr`.
4. Turtle is the readable syntax: prefixes, `;`, `,` and `a`.
5. Turtle is the source of truth. Other formats are generated.

**Try.** Create a folder `data/examples`, type the four-line Turtle example from `STUDY_GUIDE.md` Part 2 into `hello.ttl` yourself, and load it with `load_graph`.
**Say aloud.** What is a triple? Why URIs?

## Phase 1. The SKOS thesaurus

**Built.** 68 concepts in six groups with labels in three languages, definitions, hierarchy, related links, sources and 19 EuroVoc alignments.
**Why.** Terms with translations are SKOS territory, and aligning with EuroVoc makes the vocabulary interoperable.

**Five ideas.**
1. `prefLabel`: one per language. `altLabel`: any other name.
2. `broader` and `narrower` mean "belongs under", not "is a".
3. `ConceptScheme` is the whole vocabulary, `hasTopConcept` its entry points.
4. `exactMatch`, `closeMatch` and `broadMatch` link to other vocabularies, and the choice is a judgment.
5. Translations I could not confirm are flagged `pendingReview`, and 10 concepts take EuroVoc labels instead.

**To review.** `docs/translations_to_review.md` lists every French and German label that needs a native speaker.
**Say aloud.** Why is broader not subclass? How do you choose between exact and close match?

## Phase 2. The OWL ontology

**Built.** Classes and properties for legal acts with domain, range, inverse, asymmetric and functional properties, a sub-property and disjoint classes.
**Why.** To describe the acts and their relations in a way a reasoner can check and extend.

**Five ideas.**
1. A class is a kind of thing, a property a relation.
2. Domain and range say what is at each end of a property.
3. Inverse properties are the same link read backwards.
4. A sub-property implies its parent: `regulates` implies `hasTopic`.
5. Disjoint classes cannot share a member, so a reasoner can detect a contradiction.

**Try.** `python -m semlab reason` and find the three kinds of inference.
**Say aloud.** SKOS or OWL, when? What is the open world assumption?

## Phase 3. The dataset and the DCAT catalog

**Built.** 20 acts with CELEX, ELI, official title, date, topics and relations, three datasets with nine distributions, and generated JSON-LD and RDF/XML.
**Why.** To show linked data about real legislation and open data publishing.

**Five ideas.**
1. CELEX identifies an act in EUR-Lex, ELI is a permanent web address for legislation.
2. All identifiers were checked against the Cellar endpoint.
3. DCAT has three levels: catalog, dataset, distribution.
4. Shared code lists (language, theme, file type, license) make metadata understandable by other portals.
5. FAIR: Findable, Accessible, Interoperable, Reusable. Our data is CC BY 4.0.

**Try.** `python -m semlab verify-acts` (needs internet).
**Say aloud.** What is DCAT-AP? Why a code list and not free text?

## Phase 4. SPARQL

**Built.** 15 queries from easy to advanced, each with a header and a test for the documented result.
**Why.** To ask questions of the data and to use queries as data quality checks.

**Five ideas.**
1. A query is a pattern of triples with variables.
2. `FILTER` narrows, `OPTIONAL` keeps rows with missing parts.
3. Property paths: `+` one or more steps, `*` zero or more, `|` alternatives.
4. `GROUP BY` with `COUNT` counts per group.
5. `FILTER NOT EXISTS` finds what is missing.

**Try.** Write the three exercises at the end of `docs/sparql_walkthrough.md` yourself before looking at the answers.
**Say aloud.** What does `skos:broader+` do? Why does query 11 use `hasTopic|regulates`?

## Phase 5. SHACL

**Built.** Shapes for concepts, acts, datasets, distributions, catalogs and agents. Nine deliberately broken files.
**Why.** Data quality must be checkable by a machine, and a rule that never fails proves nothing.

**Five ideas.**
1. A shape describes valid data.
2. A violation fails, a warning does not.
3. SHACL treats missing data as an error, OWL does not.
4. A SPARQL constraint lets SHACL check things like unique labels across concepts.
5. Negative tests prove that each rule catches its mistake.

**Try.** In the app, Data Quality tab, break the data and read each message.
**Say aloud.** SHACL versus OWL? How do you know a rule works?

## Phase 6. The app

**Built.** A Streamlit app with six tabs: Overview, Vocabulary Browser, Acts and Graph, SPARQL Playground, Data Quality, About and Method.
**Why.** So that non-technical people can use the data and see its quality.

**Five ideas.**
1. The app reads the same Turtle files, there is no second copy of the data.
2. Helper modules turn the graph into plain data, so they are testable without a browser.
3. The playground is read-only: no updates, no SERVICE, 10 seconds, 2,000 rows.
4. Empty and error states are messages, not stack traces.
5. The *pending review* chip makes uncertainty visible.

**Say aloud.** How do you keep a SPARQL playground safe?

## Phase 7. Documentation

**Built.** README, a guide for non-technical users, how to add a concept, a 30 minute workshop outline, modeling decisions, sources and licenses, interview questions and a demo script.
**Why.** The role includes documentation and training, and a stranger should understand the project in two minutes.

**Five ideas.**
1. Write down decisions with reasons and costs.
2. Say what you verified and what you did not.
3. Test your own instructions (the how-to guide had a gap that a test found).
4. Separate the guide for users from the notes for developers.
5. State limits openly: translations, content negotiation, EuroVoc terms.

## Phase 8. Optional work

**Built.** A Cellar module with timeout, retry, cache and clear errors, used by `verify-acts`.
**Not built.** Fuseki with Docker Compose, because Docker is not installed on the development machine and an untested file would break the rule that everything must run.

**Say aloud.** Why cache? Why a retry? What happens when the network is down?
