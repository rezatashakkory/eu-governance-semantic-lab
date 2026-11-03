# Demo script and presentation guide

How to present this project in the interview. It contains a checklist, a 3 minute script you can say almost word for word, a 10 minute extended version, advice on how to talk about it, and answers to the awkward questions.

---

## 1. Honest framing, decide this before you walk in

You built this project with the help of an AI coding assistant, and you are learning RDF, SKOS, OWL, SPARQL and SHACL. That is fine, and it is better to say it plainly than to be caught out. A good way to put it:

> "I built this over the last few days to learn the stack by doing. I used an AI assistant to speed up drafting, and I worked through the code, the data model and the queries until I could explain every part. I am happy to go as deep as you like."

Then make that true:
- Read `STUDY_GUIDE.md` completely and pass the self-test in Part 12.
- **Write the three SPARQL exercises from Part 7 yourself.** Being able to type a query in front of someone is worth more than any screenshot.
- Open `data/vocabulary/eu-data-governance.ttl` and `data/shapes/shapes.ttl` and read a few blocks until they feel familiar.

**What not to claim.** Do not say you wrote the project alone by hand. Do not say the French and German labels are verified. Do not say it is an official or affiliated project. Do not claim you have used Fuseki, DCAT-AP validation or a production triple store.

---

## 2. Before the interview

**The day before** (about 20 minutes):

```powershell
cd "D:\Github Projects\eu-governance-semantic-lab"
.\.venv\Scripts\Activate.ps1
python -m pytest -q                       # should end with all tests passing
python -m semlab validate                 # SHACL: conforms
python -m streamlit run app/streamlit_app.py
```

Open each tab once so you know where things are. Stop the app with Ctrl+C.

**One hour before:**
- Laptop charged, charger in the bag, notifications off.
- Start the app and leave it open in the browser: <http://localhost:8501>. Wait for the Overview to show *Conforms*.
- Browser zoom at 110 or 125 percent so the screen is readable when shared.
- A terminal open in the project folder, virtual environment active.
- Open these in editor tabs: `data/vocabulary/eu-data-governance.ttl`, `queries/11_acts_by_topic_with_narrower.rq`, `data/shapes/shapes.ttl`.
- Close everything else. No personal tabs.

**If you are online:** you can also show the GitHub repository. If you are not, nothing breaks, because the app needs no internet. Only `python -m semlab verify-acts` does.

**If the app will not start:** the screenshots in `docs/img` show every tab. Say "let me show you the screenshots and then the same thing from the command line" and use `python -m semlab queries 11` and `python -m semlab validate`.

---

## 3. The 3 minute script

Times are a guide. Practice it out loud twice with a timer.

### 0:00 to 0:30, the pitch (Overview tab)

> "This is a small linked data stack about EU data and AI regulation. It has a multilingual thesaurus of 68 concepts in English, French and German, an OWL ontology for legal acts, a dataset of 20 real EU acts with CELEX numbers and ELI identifiers, a DCAT description of the datasets, SHACL quality rules and 15 documented SPARQL queries. Everything is plain Turtle in git, and this app reads the files live. The numbers at the top come from the data, and *Conforms* means the quality rules pass."

### 0:30 to 1:15, the thesaurus (Vocabulary Browser)

Search for `breach`, open *Personal data breach*. Then open *Data subject*.

> "Each concept has a definition, labels in three languages and broader, narrower and related links. This one shows a yellow chip, *pending review*: I am not a native French or German speaker, so I flag every translation that did not come from EuroVoc and I list them in a file for a native speaker to check. Ten concepts take their labels straight from EuroVoc, and 19 concepts link to EuroVoc with exact, close or broad match. I chose the link type for each one myself, and I would want a EuroVoc expert to review them."

### 1:15 to 1:45, the acts and the graph (Acts and Graph)

> "These are 20 real acts. Every CELEX number, ELI, title and date was checked against the Publications Office's Cellar endpoint, not typed from memory, and a command, `verify-acts`, can repeat that check. The graph shows the legal relations, for example the NIS2 Directive and the eIDAS 2 Regulation both amend the original eIDAS Regulation. The green topics link the legislation to the thesaurus."

### 1:45 to 2:15, SPARQL (SPARQL Playground)

Choose query 11 and press Run.

> "This query answers: which acts cover data protection, including every narrower topic? It joins the dataset to the thesaurus through a property path. All 15 queries have a purpose and an expected result, and each has a test that checks that result."

### 2:15 to 2:45, data quality (Data Quality tab)

Pick *celex pattern* in the broken example list and press the button.

> "SHACL is how I protect quality. These shapes require, for example, an English label and a definition for every concept, a valid CELEX pattern and a license and publisher on every dataset. A rule that never fails proves nothing, so I wrote deliberately broken data. Here the CELEX number is wrong, and the check catches it. I also use OWL reasoning, which adds facts such as 'every regulation is a legal act', but OWL cannot say a property is required. SHACL does that."

### 2:45 to 3:00, close

> "What I would do next is have the translations reviewed, publish the data with content negotiation, and add a Fuseki endpoint. For this role the interesting part for me is the same loop you work on: model, publish, check quality, and explain it to people who are not technical, which is why there is also a guide and a 30 minute workshop outline in the repository."

---

## 4. The 10 minute version

If they give you more time, add these, in this order of value:

1. **Show the Turtle** (`eu-data-governance.ttl`) next to the card. "This is the source of truth. The card is just a view of this."
2. **Run `python -m semlab reason`** in the terminal and explain one inferred triple.
3. **Open `queries/05_all_descendants.rq`** and explain the `+` in the property path. Then type your own query from the exercises.
4. **Open `docs/modeling_decisions.md`** and talk through D1 (SKOS or OWL) and D4 (URI design and the limit of a static site).
5. **Show `docs/ontology.html`**, the generated ontology documentation.
6. **Show `docs/guide_for_non_technical_users.md`** and `docs/training_workshop_30min.md`: "I wrote the documentation for the people who would use this, because the role includes training."

If you only have five minutes, do the 3 minute script and take questions.

---

## 5. How to talk about it

- **Lead with the problem, not the technology.** The problem is that the same idea has different names across languages and systems, and data quality needs automatic checks.
- **Say what you verified and what you did not.** This builds trust faster than a perfect story. Use the phrase "pending review" naturally.
- **Keep answers short, then stop.** One or two sentences, then "would you like me to go deeper?"
- **If you do not know, say so and say how you would find out.** "I have not used that. I would start with the W3C DCAT-AP specification and the validation shapes the EU publishes."
- **Connect to their work.** The Publications Office uses RDF, SKOS, OWL, DCAT-AP, ELI and EuroVoc in its own publishing. Your project uses the same standards on a small scale.
- **Show a mistake you fixed.** Real story: the first SHACL rule for unique labels took ten seconds per run because it compared every label with every other. Rewriting it as an indexed lookup made it twelve times faster. Another: the how-to guide claimed a check existed that did not, so a test caught it and a rule was added.

---

## 6. Awkward questions, and safe answers

**"Is this an official EU project?"**
No. It is an independent learning project that uses only public sources, and the disclaimer is in the README and the app.

**"Did you write all this yourself?"**
Use the framing in section 1. Do not claim more than is true.

**"Are your French and German labels correct?"**
"Ten come straight from EuroVoc. The rest I flagged as pending review, and there is a generated list of them. I would not publish them without a native speaker's check."

**"Why SKOS and not just OWL?"**
Terms with translations and hierarchy are SKOS territory, and EuroVoc is SKOS. OWL's subclass means "is a kind of", but a broader concept in a thesaurus often means "belongs under". *Right to erasure* is not a kind of *Data subject*.

**"Your URIs are on github.io. Do they dereference?"**
"They are stable names, but a static site cannot do content negotiation, so they do not return RDF by themselves. The files are published in `data/dist`. With a real service I would use a persistent redirect or a server that negotiates content. It is written up in the modeling decisions."

**"How do you know the CELEX numbers are right?"**
"I queried the Cellar SPARQL endpoint for each one and compared title, date and ELI. The command `python -m semlab verify-acts` repeats it."

**"What is the difference between SHACL and OWL?"**
OWL infers facts under the open world assumption. SHACL checks that data is complete and well formed. Use OWL for meaning and SHACL for quality.

**"Is this DCAT-AP compliant?"**
"It is DCAT-AP style. It follows the structure and uses the EU code lists, but I have not run an official DCAT-AP validation, so I do not claim conformance."

**"What is the scale limit?"**
"It is 1,306 triples in memory, which is tiny. For millions of triples I would use a triple store such as Fuseki or Virtuoso. I did not set one up, because I could not test it on my machine."

**"What would you do differently?"**
"Review the translations with native speakers. Cite articles, not only whole acts. Add a real endpoint with content negotiation. Register the catalog in a portal."

**"Which part are you least sure about?"**
"The EuroVoc match types. I chose them by comparing meanings, and a EuroVoc expert should check them."

---

## 7. Cheat sheet to keep beside you

**Numbers.** 68 concepts, 6 top concepts. 3 languages. 58 concepts with translations pending review, 10 with EuroVoc labels. 19 EuroVoc links (10 exact, 4 close, 5 broad). 20 acts (12 regulations, 7 directives, 1 implementing regulation). 6 legal relations. 15 queries. 1,306 triples. 46 triples inferred by reasoning. 9 broken test files.

**Commands.**

```powershell
python -m streamlit run app/streamlit_app.py
python -m semlab validate
python -m semlab queries 11
python -m semlab reason
python -m semlab verify-acts          # needs internet
python -m pytest -q
```

**Files to open.** `data/vocabulary/eu-data-governance.ttl`, `data/ontology/legal-acts.ttl`, `data/shapes/shapes.ttl`, `queries/11_acts_by_topic_with_narrower.rq`, `docs/modeling_decisions.md`, `docs/ontology.html`.

**One sentence per standard.**
- **RDF**: facts as subject, predicate, object, named with URIs.
- **SKOS**: terms, translations and broader or narrower links.
- **OWL**: classes and properties with logic, so a reasoner can infer.
- **SHACL**: rules the data must follow.
- **SPARQL**: questions to the data.
- **DCAT**: describing datasets so others can find and reuse them.
