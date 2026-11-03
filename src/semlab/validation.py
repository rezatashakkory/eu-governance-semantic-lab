"""SHACL validation of the project data."""

from dataclasses import dataclass, field

from pyshacl import validate
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, SH

from semlab.loading import SHAPES_FILE, load_graph


@dataclass(frozen=True)
class Finding:
    """One validation result in a simple, readable form."""

    severity: str  # "Violation" or "Warning"
    focus: str  # the node that has the problem
    path: str  # the property that has the problem, if any
    message: str
    shape: str  # the shape that reported it


@dataclass
class ValidationResult:
    conforms: bool
    findings: list[Finding] = field(default_factory=list)
    report_text: str = ""
    report_graph: Graph | None = None

    @property
    def violations(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "Violation"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "Warning"]


def _short(node) -> str:
    return str(node).rsplit("/", 1)[-1].rsplit("#", 1)[-1] if node is not None else ""


def validate_graph(data: Graph, shapes: Graph | None = None) -> ValidationResult:
    """Validate a data graph against the shapes.

    The data graph should include the ontology, so that subclasses such as
    lab:Regulation are known to be lab:LegalAct. Warnings do not make validation fail.
    """
    shapes = shapes if shapes is not None else load_graph(SHAPES_FILE)
    conforms, report_graph, report_text = validate(
        data,
        shacl_graph=shapes,
        inference="none",
        allow_warnings=True,
        meta_shacl=False,
        advanced=False,
    )
    findings = []
    for result in report_graph.subjects(RDF.type, SH.ValidationResult):
        severity = _short(report_graph.value(result, SH.resultSeverity))
        message = report_graph.value(result, SH.resultMessage)
        path = report_graph.value(result, SH.resultPath)
        findings.append(
            Finding(
                severity=severity,
                focus=str(report_graph.value(result, SH.focusNode)),
                path=_short(path) if isinstance(path, URIRef) else "",
                message=str(message) if message else "",
                shape=_short(report_graph.value(result, SH.sourceShape)),
            )
        )
    findings.sort(key=lambda f: (f.severity != "Violation", f.focus, f.message))
    return ValidationResult(bool(conforms), findings, report_text, report_graph)
