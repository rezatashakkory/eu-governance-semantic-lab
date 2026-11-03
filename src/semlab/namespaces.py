"""Namespaces and base URIs used across the project.

All identifiers for things we describe live under one base URI. The base is a GitHub
Pages address, which is stable but static: it cannot do content negotiation, so the
URIs identify things but do not return different formats on request. See
docs/modeling_decisions.md.
"""

from rdflib import Namespace
from rdflib.namespace import DCAT, DCTERMS, FOAF, OWL, RDF, RDFS, SH, SKOS, XSD

BASE = "https://rezatashakkory.github.io/eu-governance-semantic-lab/"

LAB = Namespace(BASE + "def/")  # ontology terms: classes and properties
CPT = Namespace(BASE + "id/concept/")  # thesaurus concepts
SCHEME = Namespace(BASE + "id/scheme/")
ACT = Namespace(BASE + "id/act/")
BODY = Namespace(BASE + "id/body/")
OBLIGATION = Namespace(BASE + "id/obligation/")

EUROVOC = Namespace("http://eurovoc.europa.eu/")
ELI = Namespace("http://data.europa.eu/eli/")

SCHEME_URI = SCHEME["eu-data-governance"]
LANGUAGES = ("en", "fr", "de")

# Prefixes shown in the app and used when serializing JSON-LD.
PREFIXES = {
    "lab": str(LAB),
    "cpt": str(CPT),
    "act": str(ACT),
    "skos": str(SKOS),
    "dct": str(DCTERMS),
    "dcat": str(DCAT),
    "foaf": str(FOAF),
    "owl": str(OWL),
    "rdf": str(RDF),
    "rdfs": str(RDFS),
    "sh": str(SH),
    "xsd": str(XSD),
}
