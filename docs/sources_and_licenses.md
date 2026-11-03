# Sources and licenses

## Licenses of this repository

| Part | License |
| --- | --- |
| Source code: `src/`, `app/`, `tests/`, scripts, Makefile | MIT, see `LICENSE` |
| Data and documentation: `data/`, `queries/`, `docs/` | Creative Commons Attribution 4.0 International (CC BY 4.0), legal text at <https://creativecommons.org/licenses/by/4.0/legalcode> |

CC BY 4.0 covers the original work in this project: the thesaurus structure, definitions, the ontology, the selection and linking of acts, the shapes and the queries. It does not change the terms of third-party material listed below.

## What came from where

Every fact that comes from outside the project was checked on **3 November 2026**.

| Content | Source | How it was checked |
| --- | --- | --- |
| CELEX numbers, ELI identifiers, official English titles, document dates of the 20 acts | Cellar, the repository of the Publications Office of the EU, public SPARQL endpoint <https://publications.europa.eu/webapi/rdf/sparql> | Queried directly. Re-checkable at any time with `python -m semlab verify-acts`. |
| Legal relations: 3 amends, 2 repeals, 1 is based on | Same endpoint, properties `cdm:resource_legal_amends_resource_legal`, `cdm:resource_legal_repeals_resource_legal`, `cdm:resource_legal_based_on_resource_legal` | Queried among the 20 acts |
| EuroVoc concept URIs, and the French and German labels of 10 concepts | EuroVoc, queried through the same endpoint | Each of the 19 URIs was returned with a matching English label |
| Language, data theme, file type, license and frequency codes in the DCAT catalog | EU Vocabularies authority tables, <http://publications.europa.eu/resource/authority/> | Each code was returned by the endpoint with an English label |
| That the European Data Protection Board and the European Artificial Intelligence Board are established by their acts, and that the Data Governance Act requires the Commission to set up the European Data Innovation Board as an expert group | GDPR Article 68, AI Act Article 65, Data Governance Act Article 29 | Checked on web pages that reproduce the article texts. The EUR-Lex text is the authoritative source and was not read directly, because EUR-Lex blocks scripted access. The Data Innovation Board is modeled with "provides for", not "establishes". |
| W3C and other specifications cited in definitions | <https://www.w3.org/TR/vocab-dcat-3/>, <https://www.w3.org/DesignIssues/LinkedData.html>, <https://doi.org/10.1038/sdata.2016.18> | Each address was requested and answered |

## What was written for this project

- The 68 concept definitions, the English, French and German labels that are not from EuroVoc, the alternative labels, the hierarchy and the related links.
- The short names of acts such as GDPR or AI Act. They are informal and are not part of the official titles.
- The three obligation summaries and the descriptions in the ontology.
- The links from acts to thesaurus topics.

Definitions are plain-language explanations. They are **not legal text** and must not be used as legal advice.

## Terms of use of third-party material

- **EU legal acts and Cellar metadata.** Only identifiers, titles and dates (metadata) are used, not the legal text. The Publications Office publishes its reuse conditions on its legal notice pages. The Cellar page of the Publications Office directs questions about reuse of Cellar and EU Vocabularies content to op-copyright@publications.europa.eu.
- **EuroVoc.** The EuroVoc dataset page on the EU Vocabularies site names the European Commission reuse notice (Decision 2011/833/EU) as its terms, which require acknowledgement of the source. This project does not copy the thesaurus. It uses 19 identifiers and 10 pairs of labels, with acknowledgement here: *EuroVoc, Publications Office of the European Union*. **The CC BY 4.0 license of this repository does not apply to those EuroVoc labels.** Check the current terms on the EuroVoc page before reusing them.
- **Not affiliated.** This is an independent learning project. It is not affiliated with, endorsed by, or an official product of the Publications Office of the European Union or any other EU institution. It uses no EU logos or brand colors.

## Not verified

- The exact current licence wording of EuroVoc: a search did not return a page stating it as CC BY 4.0, so none is claimed.
- The French and German labels not taken from EuroVoc. They are pending review, see `docs/translations_to_review.md`.
- Article-level citations for definitions. Definitions point to the act as a whole, not to a numbered article.
