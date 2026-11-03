# Guide for non-technical users

This guide is for policy officers, lawyers, librarians and anyone who works with EU legislation and wants to use this project **without writing code**. You only need a web browser.

## What this project gives you

1. A **thesaurus**: a controlled list of 68 terms about data protection, data governance, AI, open data, digital resilience and data quality, each with a definition and labels in English, French and German.
2. A **list of 20 EU acts** (for example the GDPR, the AI Act and the Data Act) with their official identifiers and the topics they cover.
3. A way to **ask questions** of this information and to **check its quality**.

## Start the app

Your colleague or administrator starts it with `python -m streamlit run app/streamlit_app.py`. A page opens in your browser. The six tabs along the top are described below.

## Tab by tab

### Overview
Shows the size of the data and whether the quality checks pass. The word **Conforms** means that every rule was met.

### Vocabulary Browser
**To find a term:**
1. Type a word in **Search**. You can search in English, French or German. The search also looks inside definitions.
2. Click a result. The right side shows the term card.

**To explore by topic:** open one of the six main groups and click through. Terms are indented under the broader term they belong to.

**What the card tells you:**
- the **definition** in plain English,
- the **labels** in three languages. The word *pending review* means a native speaker has not yet checked that translation. *From EuroVoc* means the label is the official EuroVoc label,
- **broader**, **narrower** and **related** terms, which you can click,
- **alignments to EuroVoc**: links to the matching concept in the official EU thesaurus. *Same meaning* is the strongest link, *similar meaning* is looser, and *broader* means the EuroVoc concept covers more,
- the **act** the definition is based on and the acts in this project that cover the term.

Use **Label language** in the left bar to switch the tree and card titles to French or German.

### Acts and Graph
The table lists the acts, oldest first. Use **Show types** to narrow it down. Pick an act under **Act details** to see its official title, its CELEX number (the identifier used by EUR-Lex), its ELI (a permanent web address for legislation) and a link to the text on EUR-Lex.

The **graph** shows how acts connect. Blue boxes are acts, green ellipses are topics. An arrow labeled *amends* means the act at the start changes the act at the end. You can drag boxes and zoom with the mouse wheel.

### SPARQL Playground
SPARQL is a query language. You do not have to write it. Choose one of the **15 example queries**, read the *Purpose* and *Expected result*, and press **Run query**. The result appears as a table, which you can save with **Download CSV**.

Some examples worth trying:
- *Number of acts per type* (13)
- *Acts about a topic, including narrower topics* (11)
- *Amends, repeals and is based on* (12)

If you edit a query and make a mistake, the page shows a message. The playground is read-only. It cannot change the data.

### Data Quality
Shows the result of the automatic checks, for example "every term has an English label and a definition". The section **Break the data on purpose** adds a deliberately wrong example and shows the checks failing. The last section lists how many translations still wait for review.

### About and Method
Explains the standards used, where the information comes from and what the limits are.

## Words you will meet

| Word | Meaning |
| --- | --- |
| Concept | One entry in the thesaurus, such as *Personal data*. |
| Preferred label | The main name of a concept in one language. |
| Broader, narrower | Up and down in the hierarchy. *Personal data* is narrower than *Data protection*. |
| CELEX | The number EUR-Lex gives to each act, for example 32016R0679 for the GDPR. |
| ELI | European Legislation Identifier, a permanent web address for an act. |
| EuroVoc | The multilingual thesaurus of the EU institutions, maintained by the Publications Office. |
| Triple | The basic unit of the data: a subject, a property and a value, such as "GDPR, has topic, Personal data". |

## What this project is not

- It is **not legal advice**. Definitions are plain-language explanations written for this project.
- It is **not an official EU product**. It is an independent learning project and is not affiliated with any EU institution.
- French and German labels marked *pending review* may contain mistakes.

## Found a mistake?

Tell the maintainer which term and which language. To fix it yourself, see `docs/how_to_add_a_concept.md`.
