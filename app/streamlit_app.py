"""EU Data Governance Semantic Lab: explore the thesaurus, the acts, SPARQL and data quality.

Independent learning project. Not affiliated with or endorsed by the Publications Office
of the European Union or any other EU institution.
"""

from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, SKOS

from semlab import acts, vocabulary
from semlab.loading import ONTOLOGY_FILE, load_all, load_graph
from semlab.namespaces import CPT, LANGUAGES
from semlab.queries import QueryError, QueryTimeout, list_queries, run_query
from semlab.reasoning import expand, inconsistencies
from semlab.validation import validate_graph

TEST_DATA = Path(__file__).resolve().parent.parent / "tests" / "data"
LANGUAGE_NAMES = {"en": "English", "fr": "Français", "de": "Deutsch"}
DEEP_BLUE = "#1E3A5F"
TEAL = "#0F766E"

st.set_page_config(
    page_title="EU Data Governance Semantic Lab",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
    .block-container {{ padding-top: 2rem; max-width: 1200px; }}
    h1, h2, h3 {{ color: {DEEP_BLUE}; letter-spacing: -0.01em; }}
    h1 {{ font-weight: 700; margin-bottom: 0.25rem; }}
    .lab-caption {{ color: #475569; font-size: 1rem; margin-bottom: 1rem; }}
    .lab-disclaimer {{
        background: #F1F5F9; border-left: 4px solid {TEAL}; padding: 0.6rem 0.9rem;
        border-radius: 4px; font-size: 0.85rem; color: #334155; margin-bottom: 1.2rem;
    }}
    .lab-card {{
        border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.1rem 1.3rem;
        background: #FFFFFF; margin-bottom: 1rem;
    }}
    .lab-def {{ font-size: 1.05rem; line-height: 1.55; color: #14263F; }}
    .lab-chip {{
        display: inline-block; padding: 0.1rem 0.55rem; border-radius: 999px;
        font-size: 0.75rem; font-weight: 600; margin-left: 0.4rem;
    }}
    .lab-chip-warn {{ background: #FEF3C7; color: #92400E; }}
    .lab-chip-ok {{ background: #CCFBF1; color: #115E59; }}
    .lab-chip-info {{ background: #DBEAFE; color: #1E3A8A; }}
    .lab-muted {{ color: #64748B; font-size: 0.9rem; }}
    div[data-testid="stMetric"] {{
        background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 0.8rem 1rem;
    }}
    .stButton > button, .stButton > button > div {{
        justify-content: flex-start !important; text-align: left !important;
    }}
    .stButton > button p {{ text-align: left !important; }}
    button[data-baseweb="tab"] {{ font-weight: 600; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------- data


@st.cache_resource(show_spinner="Loading the data")
def get_graph() -> Graph:
    return load_all()


@st.cache_resource(show_spinner="Running SHACL validation")
def get_validation():
    return validate_graph(get_graph())


@st.cache_resource(show_spinner="Running the OWL RL reasoner")
def get_inferred() -> Graph:
    return expand(get_graph(), load_graph(ONTOLOGY_FILE))[1]


def load_or_stop() -> Graph:
    try:
        return get_graph()
    except Exception as error:  # a broken data file should not show a stack trace
        st.error(f"The data could not be loaded. Check the Turtle files. Details: {error}")
        st.stop()


def chip(text: str, kind: str = "info") -> str:
    return f'<span class="lab-chip lab-chip-{kind}">{text}</span>'


# ---------------------------------------------------------------------------- tabs


def render_overview(graph: Graph) -> None:
    st.subheader("What this is")
    st.write(
        "A small linked data stack about EU data and AI regulation. It combines a multilingual "
        "SKOS thesaurus, an OWL ontology for legal acts, a dataset of 20 real EU acts with "
        "official identifiers, DCAT metadata, SHACL data quality shapes and 15 documented "
        "SPARQL queries. Everything is plain RDF in Turtle files, and this app reads them live."
    )
    validation = get_validation()
    concepts = len(set(graph.subjects(RDF.type, SKOS.Concept)))
    columns = st.columns(5)
    columns[0].metric("Concepts", concepts)
    columns[1].metric("Legal acts", len(acts.act_nodes(graph)))
    columns[2].metric("Triples", f"{len(graph):,}")
    columns[3].metric("SPARQL queries", len(list_queries()))
    columns[4].metric("SHACL", "Conforms" if validation.conforms else "Fails")

    st.subheader("How the pieces fit")
    st.graphviz_chart(
        """
        digraph G {
            rankdir=LR; bgcolor="transparent";
            node [shape=box, style="rounded,filled", fillcolor="#E6F4F1", color="#0F766E",
                  fontname="Helvetica", fontsize=11, margin="0.15,0.08"];
            edge [color="#64748B"];
            ttl [label="Turtle files\\n(source of truth)", fillcolor="#DBEAFE", color="#1E3A5F"];
            g [label="RDF graph\\n(rdflib)"];
            shacl [label="SHACL\\n(pySHACL)"];
            owl [label="OWL RL reasoning\\n(owlrl)"];
            sparql [label="SPARQL\\n(15 queries)"];
            dist [label="JSON-LD and RDF/XML\\n(data/dist)"];
            app [label="This app", fillcolor="#DBEAFE", color="#1E3A5F"];
            ttl -> g; g -> shacl; g -> owl; g -> sparql; ttl -> dist;
            shacl -> app; owl -> app; sparql -> app;
        }
        """,
        use_container_width=True,
    )

    st.subheader("Where to start")
    st.markdown(
        "- **Vocabulary Browser**: open *Data protection* and follow the tree, switch the language, "
        "and look at the EuroVoc alignments.\n"
        "- **Acts and Graph**: see how the 20 acts amend, repeal and connect to topics.\n"
        "- **SPARQL Playground**: run query 11 to find acts about a topic and all its narrower topics.\n"
        "- **Data Quality**: run the SHACL checks, then break the data on purpose and watch them fail."
    )


def select_concept(uri: str) -> None:
    st.session_state["selected"] = uri


def flatten(nodes, depth=0):
    for node in nodes:
        yield node, depth
        yield from flatten(node.children, depth + 1)


def render_tree_button(node, depth: int) -> None:
    slug = vocabulary.short_name(node.uri)
    selected = st.session_state.get("selected") == str(node.uri)
    holder = st.container()
    if depth:
        _, holder = st.columns([depth, 14 - depth], gap="small")
    holder.button(
        node.label,
        key=f"tree_{slug}",
        on_click=select_concept,
        args=(str(node.uri),),
        use_container_width=True,
        type="primary" if selected else "secondary",
    )


def concept_link_buttons(items, prefix: str) -> None:
    for uri, text in items:
        st.button(
            text,
            key=f"{prefix}_{vocabulary.short_name(uri)}",
            on_click=select_concept,
            args=(str(uri),),
        )


def render_card(graph: Graph, uri: str, lang: str) -> None:
    card = vocabulary.concept_card(graph, URIRef(uri), lang)
    pending = card["pending_review"]
    header = f"<h2 style='margin:0'>{card['label']}</h2>"
    st.markdown(header, unsafe_allow_html=True)
    st.caption(f"URI: `{card['uri']}`")
    st.markdown(f"<div class='lab-card lab-def'>{card['definition']}</div>", unsafe_allow_html=True)

    st.markdown("**Labels**")
    rows = []
    for code in LANGUAGES:
        text = card["labels"].get(code, "")
        status = ""
        if code != "en":
            status = "pending review" if code in pending else "from EuroVoc"
        rows.append({"Language": LANGUAGE_NAMES[code], "Preferred label": text, "Status": status})
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    if pending:
        st.markdown(
            chip("Translations pending review", "warn")
            + " <span class='lab-muted'>A native speaker has not checked the French and German "
            "labels of this concept yet.</span>",
            unsafe_allow_html=True,
        )
    if card["alt_labels"]:
        st.markdown("**Alternative labels:** " + ", ".join(card["alt_labels"]))

    columns = st.columns(3)
    with columns[0]:
        st.markdown("**Broader**")
        if card["broader"]:
            concept_link_buttons(card["broader"], "up")
        else:
            st.caption("None, this is a top concept.")
    with columns[1]:
        st.markdown("**Narrower**")
        if card["narrower"]:
            concept_link_buttons(card["narrower"], "down")
        else:
            st.caption("None.")
    with columns[2]:
        st.markdown("**Related**")
        if card["related"]:
            concept_link_buttons(card["related"], "rel")
        else:
            st.caption("None.")

    st.markdown("**Alignments to EuroVoc**")
    if card["alignments"]:
        meaning = {
            "exactMatch": "same meaning",
            "closeMatch": "similar meaning",
            "broadMatch": "EuroVoc concept is broader",
        }
        for a in card["alignments"]:
            st.markdown(f"- `skos:{a['type']}` ({meaning[a['type']]}): [{a['uri']}]({a['uri']})")
    else:
        st.caption("No verified alignment for this concept.")

    st.markdown("**Sources and legal acts**")
    if card["sources"]:
        st.markdown("Definition based on: " + "; ".join(s["text"] for s in card["sources"]))
    if card["acts"]:
        st.markdown(
            "Acts in this lab that cover it: " + ", ".join(name for _, name in card["acts"])
        )
    if not card["sources"] and not card["acts"]:
        st.caption("No source act. This is a general data management concept.")


def render_vocabulary(graph: Graph, lang: str) -> None:
    st.session_state.setdefault("selected", str(CPT["data-protection"]))
    left, right = st.columns([2, 3], gap="large")
    with left:
        query = st.text_input(
            "Search",
            placeholder="Try: breach, Daten, données, API",
            help="Searches labels in all three languages, alternative labels and definitions.",
        )
        if query.strip():
            hits = vocabulary.search(graph, query, lang)
            if not hits:
                st.info(f"No concept matches '{query}'. Try a shorter word or another language.")
            else:
                st.caption(f"{len(hits)} concept(s) found")
                for concept in hits:
                    st.button(
                        vocabulary.label(graph, concept, lang),
                        key=f"hit_{vocabulary.short_name(concept)}",
                        on_click=select_concept,
                        args=(str(concept),),
                        use_container_width=True,
                    )
        else:
            selected = st.session_state["selected"]
            for top in vocabulary.tree(graph, lang):
                members = [n.uri for n, _ in flatten([top])]
                with st.expander(top.label, expanded=any(str(m) == selected for m in members)):
                    for node, depth in flatten([top]):
                        render_tree_button(node, depth)
    with right:
        render_card(graph, st.session_state["selected"], lang)


def render_acts(graph: Graph, lang: str) -> None:
    rows = acts.acts_table(graph, lang)
    types = sorted({r["type"] for r in rows})
    chosen = st.multiselect("Show types", types, default=types)
    shown = [r for r in rows if r["type"] in chosen]
    if not shown:
        st.info("No act matches the filter. Select at least one type.")
        return
    frame = pd.DataFrame(
        [
            {
                "Short name": r["short_name"],
                "Type": r["type"],
                "Date": r["date"],
                "CELEX": r["celex"],
                "Main subject": ", ".join(r["regulates"]),
                "Relations": "; ".join(f"{x['relation']} {x['target']}" for x in r["relations"]),
            }
            for r in shown
        ]
    )
    st.dataframe(frame, hide_index=True, use_container_width=True)

    names = [f"{r['short_name']} ({r['celex']})" for r in shown]
    pick = st.selectbox("Act details", names)
    row = shown[names.index(pick)]
    st.markdown(f"<div class='lab-card'><b>{row['title']}</b></div>", unsafe_allow_html=True)
    st.markdown(
        f"**CELEX** `{row['celex']}`  \n**ELI** [{row['eli']}]({row['eli']})  \n"
        f"**EUR-Lex** [open the text]({row['eur_lex']})  \n"
        f"**Topics** {', '.join(row['topics']) or 'none'}"
    )

    st.subheader("Graph explorer")
    with_topics = st.toggle("Show main subjects (topics)", value=True)
    nodes, edges = acts.graph_elements(graph, with_topics, lang)
    components.html(build_network_html(nodes, edges), height=660, scrolling=False)
    st.caption(
        "Blue boxes are acts, teal ellipses are topics from the thesaurus. Drag nodes, scroll to "
        "zoom, hover for the full title. Arrows read: from-act amends, repeals or is based on to-act."
    )


def build_network_html(nodes, edges) -> str:
    from pyvis.network import Network

    net = Network(
        height="640px",
        width="100%",
        bgcolor="#FFFFFF",
        font_color="#14263F",
        directed=True,
        cdn_resources="in_line",
    )
    for node_id, text, kind, tooltip in nodes:
        if kind == "act":
            net.add_node(
                node_id,
                label=text,
                title=tooltip,
                shape="box",
                color="#DBEAFE",
                borderWidth=1,
                font={"size": 18},
            )
        else:
            net.add_node(
                node_id,
                label=text,
                title=tooltip,
                shape="ellipse",
                color="#CCFBF1",
                font={"size": 16},
            )
    for source, target, text in edges:
        colour = "#94A3B8" if text == "regulates" else "#1E3A5F"
        net.add_edge(
            source,
            target,
            label=text if text != "regulates" else "",
            title=text,
            color=colour,
            font={"size": 10, "align": "middle"},
        )
    net.set_options(
        '{"layout": {"randomSeed": 11}, '
        '"physics": {"solver": "forceAtlas2Based", "forceAtlas2Based": '
        '{"gravitationalConstant": -60, "centralGravity": 0.05, "springLength": 70, '
        '"springConstant": 0.08, "damping": 0.5, "avoidOverlap": 0.8}, '
        '"stabilization": {"iterations": 300}}, '
        '"nodes": {"scaling": {"label": {"drawThreshold": 0}}}, '
        '"interaction": {"hover": true}}'
    )
    html = net.generate_html()
    # Streamlit renders inactive tabs hidden, so the graph is laid out in a frame of the wrong
    # size. Re-fit whenever the frame changes size, and stop the physics once it has settled.
    fit = (
        "<script>"
        "network.once('stabilizationIterationsDone', function () {"
        "network.setOptions({physics: false}); network.fit(); });"
        "new ResizeObserver(function () { network.redraw(); network.fit(); })"
        ".observe(document.documentElement);"
        "</script>"
    )
    return html.replace("</body>", fit + "</body>")


def render_playground(graph: Graph) -> None:
    queries = list_queries()
    labels = [f"{q.number}  {q.title}  [{q.level}]" for q in queries]
    pick = st.selectbox("Example query", labels)
    chosen = queries[labels.index(pick)]
    st.markdown(f"**Purpose.** {chosen.purpose}")
    st.markdown(f"**Expected result.** {chosen.expected}")
    st.markdown(f"**Concepts used.** {chosen.concepts}")
    text = st.text_area(
        "Query (you can edit it)",
        value=chosen.text,
        height=330,
        key=f"query_text_{chosen.number}",
    )
    st.caption(
        "Read-only: SELECT, ASK, CONSTRUCT and DESCRIBE only, no SERVICE calls, at most 2,000 rows, "
        "10 second limit."
    )
    if not st.button("Run query", type="primary"):
        return
    try:
        result = run_query(graph, text, timeout=10.0)
    except QueryTimeout as error:
        st.warning(str(error))
        return
    except QueryError as error:
        st.error(str(error))
        return
    if result.kind == "ask":
        if result.boolean:
            st.success("The answer is **true**.")
        else:
            st.info("The answer is **false**.")
    elif result.kind == "select":
        if not result.rows:
            st.info(
                "The query returned no rows. For a data quality query, no rows is the good result."
            )
            return
        frame = pd.DataFrame(result.rows, columns=result.columns)
        st.caption(f"{len(frame)} row(s)" + (", truncated at 2,000" if result.truncated else ""))
        st.dataframe(frame, hide_index=True, use_container_width=True)
        st.download_button(
            "Download CSV",
            frame.to_csv(index=False).encode("utf-8"),
            file_name=f"query_{chosen.number}.csv",
            mime="text/csv",
        )
    else:
        turtle = result.graph.serialize(format="turtle")
        st.caption(f"{len(result.graph)} triple(s) built by the query")
        st.code(turtle[:6000] + ("\n..." if len(turtle) > 6000 else ""), language="turtle")
        st.download_button(
            "Download Turtle",
            turtle.encode("utf-8"),
            file_name=f"query_{chosen.number}.ttl",
            mime="text/turtle",
        )


def show_findings(result) -> None:
    if result.conforms:
        st.success(
            f"Conforms. {len(result.violations)} violation(s), {len(result.warnings)} warning(s)."
        )
    else:
        st.error(f"Does not conform. {len(result.violations)} violation(s).")
    if result.findings:
        frame = pd.DataFrame(
            [
                {
                    "Severity": f.severity,
                    "Node": vocabulary.short_name(f.focus),
                    "Property": f.path,
                    "Problem": f.message,
                }
                for f in result.findings
            ]
        )
        st.dataframe(frame, hide_index=True, use_container_width=True)


def render_quality(graph: Graph) -> None:
    st.subheader("1. SHACL validation of the published data")
    st.write(
        "SHACL shapes describe what valid data looks like. The checks include an English label "
        "and a definition for every concept, one preferred label per language, a valid CELEX "
        "pattern, and a license and publisher for every dataset."
    )
    show_findings(get_validation())

    st.subheader("2. Break the data on purpose")
    st.write(
        "Add one deliberately wrong file to the data and validate again. Eight of the nine "
        "examples must fail. The missing translations example only gives warnings."
    )
    files = sorted(TEST_DATA.glob("broken_*.ttl")) if TEST_DATA.exists() else []
    if not files:
        st.info("The test data folder is not available in this deployment.")
    else:
        names = [f.stem.replace("broken_", "").replace("_", " ") for f in files]
        pick = st.selectbox("Broken example", names)
        path = files[names.index(pick)]
        st.code(path.read_text(encoding="utf-8").split("\n\n", 1)[-1].strip(), language="turtle")
        if st.button("Validate with this example added"):
            combined = Graph()
            for triple in graph:
                combined.add(triple)
            combined += load_graph(path)
            show_findings(validate_graph(combined))

    st.subheader("3. Reasoning")
    st.write(
        "OWL RL reasoning adds facts that follow from the ontology. For example, every regulation "
        "is also a legal act, and 'regulates' implies 'has topic'."
    )
    problems = inconsistencies(graph)
    if problems:
        st.error(" ".join(problems))
    else:
        st.success("No contradictions found in the data.")
    inferred = get_inferred()
    short = graph.namespace_manager.normalizeUri
    frame = pd.DataFrame(
        sorted(tuple(short(x) for x in triple) for triple in inferred),
        columns=["Subject", "Predicate", "Object"],
    )
    with st.expander(f"{len(frame)} triples inferred by the reasoner"):
        st.dataframe(frame, hide_index=True, use_container_width=True)

    st.subheader("4. Translations waiting for review")
    pending = vocabulary.pending_review(graph)
    columns = st.columns(len(pending))
    for column, (code, concepts) in zip(columns, pending.items(), strict=True):
        column.metric(f"{LANGUAGE_NAMES[code]} concepts pending", len(concepts))
    st.caption(
        "Concepts whose labels come from EuroVoc are not counted. The full list is in "
        "docs/translations_to_review.md."
    )


def render_about() -> None:
    st.subheader("Concepts")
    st.markdown(
        "- **RDF** describes facts as triples: subject, predicate, object. Names are URIs.\n"
        "- **SKOS** models vocabularies: concepts, labels in many languages, broader and narrower "
        "links. Use it for *terms and their meaning*.\n"
        "- **OWL** models classes and properties with logic, so a reasoner can infer new facts. "
        "Use it for *things and their relations*.\n"
        "- **SHACL** checks data against shapes. OWL infers, SHACL validates.\n"
        "- **SPARQL** is the query language for RDF.\n"
        "- **DCAT** describes datasets and distributions, the basis of open data catalogs."
    )
    st.subheader("Sources")
    st.markdown(
        "- Act identifiers, titles, dates and legal relations: public Cellar SPARQL endpoint of the "
        "Publications Office of the EU, checked on 2026-11-03.\n"
        "- Alignments and the French and German labels of ten concepts: EuroVoc, looked up through "
        "the same endpoint.\n"
        "- Code lists for languages, themes, file types and licenses: EU Vocabularies authority tables.\n"
        "- Specifications: W3C RDF, SKOS, OWL 2, SHACL, SPARQL 1.1 and DCAT."
    )
    st.subheader("Limits")
    st.markdown(
        "- French and German labels not taken from EuroVoc are marked **pending review**.\n"
        "- Definitions are written for this project in plain English and are not legal text.\n"
        "- Identifiers use a GitHub Pages address. A static site cannot do content negotiation, so "
        "the URIs name things but do not return different formats on request."
    )
    st.subheader("License and disclaimer")
    st.markdown(
        "Code is MIT. Data is CC BY 4.0. This is an independent learning project. It is not "
        "affiliated with, endorsed by, or an official product of the Publications Office of the "
        "European Union or any other EU institution."
    )


# ---------------------------------------------------------------------------- page

graph = load_or_stop()

st.title("EU Data Governance Semantic Lab")
st.markdown(
    "<div class='lab-caption'>A small linked data stack on EU data and AI regulation: SKOS, OWL, "
    "SHACL, SPARQL and DCAT.</div>"
    "<div class='lab-disclaimer'>Independent learning project. Not affiliated with, endorsed by, "
    "or an official product of the Publications Office of the European Union or any other EU "
    "institution.</div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Display")
    language = st.selectbox(
        "Label language",
        list(LANGUAGES),
        format_func=lambda code: LANGUAGE_NAMES[code],
        help="Used for concept labels in the browser, the tree and the graph.",
    )
    st.caption("Definitions and interface text are in English.")

tab_overview, tab_vocab, tab_acts, tab_sparql, tab_quality, tab_about = st.tabs(
    [
        "Overview",
        "Vocabulary Browser",
        "Acts and Graph",
        "SPARQL Playground",
        "Data Quality",
        "About and Method",
    ]
)
with tab_overview:
    render_overview(graph)
with tab_vocab:
    render_vocabulary(graph, language)
with tab_acts:
    render_acts(graph, language)
with tab_sparql:
    render_playground(graph)
with tab_quality:
    render_quality(graph)
with tab_about:
    render_about()
