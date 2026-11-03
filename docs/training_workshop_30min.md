# Workshop outline: linked data for non-technical colleagues (30 minutes)

**Audience.** People who work with EU legislation or documents and have never used RDF or SPARQL. No installation is needed if the trainer shares a screen. With a laptop each, add 10 minutes.

**Goal.** By the end, participants can say what a thesaurus is, find a term and its translations, explain why identifiers matter, and read the result of a simple query.

**Preparation.** The app runs on the trainer's machine. Open these tabs beforehand: Vocabulary Browser and SPARQL Playground. Print the glossary table from `docs/guide_for_non_technical_users.md`.

## Agenda

| Minutes | Part | What happens |
| --- | --- | --- |
| 0 to 3 | Why | The problem: the same idea has different names across languages, systems and teams. Show two spreadsheets that call the same thing different names. |
| 3 to 8 | Triples | One fact is a sentence in three parts. Draw "GDPR, has topic, Personal data" on a flip chart. Explain that each part has a permanent address, a URI. |
| 8 to 15 | Thesaurus tour | Live demo, Vocabulary Browser. Search "breach". Open *Personal data breach*. Show the French and German labels, the definition and the broader term. Switch the language to German. |
| 15 to 20 | Standards and links | Open the EuroVoc alignment on a card. Explain that linking to a shared identifier is what makes data from different publishers connect. Show the *pending review* chip and say why it is honest to show it. |
| 20 to 26 | Questions on data | SPARQL Playground. Run query 13 (acts per type), then query 11 (acts about data protection). Ask the group which question they would put to the data. |
| 26 to 30 | Quality and wrap up | Data Quality tab. Break the data on purpose and show the failure. Recap with the four questions below. |

## Exercises (for the hands-on version)

1. Find the French label of *Data portability*. (Answer: portabilité des données, still pending review.)
2. Which act repeals the Data Protection Directive of 1995? Use the Acts and Graph tab. (Answer: the GDPR.)
3. Run query 8 (missing translations). What does an empty result mean? (Answer: nothing is missing.)
4. In the Playground, change the keyword in query 3 from *incident|breach* to *risk*. How many results? (Answer: 4, High-risk AI system, ICT risk management, ICT third-party risk and Risk-based approach.)

## Four questions to close

1. What is the difference between a label and an identifier?
2. Why does a thesaurus have broader and narrower terms?
3. What does *pending review* tell the reader?
4. How would a rule such as "every term needs a definition" be checked automatically?

## Handout: the key ideas on one page

- Data about things is stored as **triples** (subject, property, value).
- Things are named with **URIs**, permanent addresses that are the same for everyone.
- A **thesaurus** (SKOS) organizes terms with labels in several languages and broader and narrower links.
- An **ontology** (OWL) describes kinds of things and how they relate, so a computer can draw conclusions.
- **SPARQL** asks questions of the data. **SHACL** checks that the data follows the rules.
- Linking your terms to a shared thesaurus such as **EuroVoc** lets other people connect their data to yours.
