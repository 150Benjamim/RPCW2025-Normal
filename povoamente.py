import json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
import os

# Ontologia base
TTL_FILE = "sapientia_base.ttl"
OUTPUT_FILE = "sapientia_ind.ttl"

# Namespaces
SAPIENTA = Namespace("http://example.org/sapienta#")
BASE = Namespace("http://www.semanticweb.org/benjamim/ontologies/2025/4/untitled-ontology-6/")

# Carregar a ontologia existente
g = Graph()
g.parse(TTL_FILE, format="ttl")
g.bind("", SAPIENTA)

def safe_uri(name):
    return URIRef(SAPIENTA + name.replace(" ", "_"))

# === Funções de criação ===
def criar_conceito(g, nome):
    conceito_uri = safe_uri(nome)
    g.add((conceito_uri, RDF.type, SAPIENTA.Conceito))
    g.add((conceito_uri, SAPIENTA.nome, Literal(nome)))
    return conceito_uri

def criar_disciplina(g, nome):
    disciplina_uri = safe_uri(nome)
    g.add((disciplina_uri, RDF.type, SAPIENTA.Disciplina))
    g.add((disciplina_uri, SAPIENTA.nome, Literal(nome)))
    return disciplina_uri

def criar_mestre(g, nome):
    mestre_uri = safe_uri(nome)
    g.add((mestre_uri, RDF.type, SAPIENTA.Mestre))
    g.add((mestre_uri, SAPIENTA.nome, Literal(nome)))
    return mestre_uri

def criar_obra(g, titulo):
    obra_uri = safe_uri(titulo)
    g.add((obra_uri, RDF.type, SAPIENTA.Obra))
    g.add((obra_uri, SAPIENTA.nome, Literal(titulo)))
    return obra_uri

def criar_aprendiz(g, nome, idade=None):
    aprendiz_uri = safe_uri(nome)
    g.add((aprendiz_uri, RDF.type, SAPIENTA.Aprendiz))
    g.add((aprendiz_uri, SAPIENTA.nome, Literal(nome)))
    if idade is not None:
        g.add((aprendiz_uri, SAPIENTA.idade, Literal(idade, datatype=XSD.int)))
    return aprendiz_uri

def criar_periodo(g, nome):
    periodo_uri = safe_uri(nome)
    g.add((periodo_uri, RDF.type, SAPIENTA.PeriodoHistorico))
    g.add((periodo_uri, SAPIENTA.nome, Literal(nome)))
    return periodo_uri

def criar_aplicacao(g, nome):
    aplicacao_uri = safe_uri(nome)
    g.add((aplicacao_uri, RDF.type, SAPIENTA.Aplicacao))
    g.add((aplicacao_uri, SAPIENTA.nome, Literal(nome)))
    return aplicacao_uri

# === Carregamento dos dados JSON ===
def load_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

conceitos = load_json("conceitos.json")["conceitos"]
disciplinas = load_json("disciplinas.json")["disciplinas"]
mestres = load_json("mestres.json")["mestres"]
obras = load_json("obras.json")["obras"]
aprendizes = load_json("pg57511.json")

# === Povoa conceitos ===
conceito_map = {}
for c in conceitos:
    conceito_uri = criar_conceito(g, c["nome"])
    conceito_map[c["nome"]] = conceito_uri

    # Aplicações
    for app in c.get("aplicações", []):
        app_uri = criar_aplicacao(g, app)
        g.add((conceito_uri, SAPIENTA.temAplicacaoEm, app_uri))

    # Período histórico
    if "períodoHistórico" in c:
        periodo_uri = criar_periodo(g, c["períodoHistórico"])
        g.add((conceito_uri, SAPIENTA.surgeEm, periodo_uri))

    # Conceitos relacionados
    for rel in c.get("conceitosRelacionados", []):
        rel_uri = conceito_map.get(rel) or criar_conceito(g, rel)
        g.add((conceito_uri, SAPIENTA.estaRelacionadoCom, rel_uri))

# === Povoa disciplinas ===
for d in disciplinas:
    disc_uri = criar_disciplina(g, d["nome"])
    for tipo in d.get("tiposDeConhecimento", []):
        tipo_uri = safe_uri(tipo)
        g.add((tipo_uri, RDF.type, SAPIENTA.TipoDeConhecimento))
        g.add((tipo_uri, SAPIENTA.nome, Literal(tipo)))
        g.add((disc_uri, SAPIENTA.pertenceA, tipo_uri))

    for conceito in d.get("conceitos", []):
        conc_uri = conceito_map.get(conceito) or criar_conceito(g, conceito)
        g.add((disc_uri, SAPIENTA.estuda, conc_uri))

# === Povoa mestres ===
for m in mestres:
    mestre_uri = criar_mestre(g, m["nome"])
    if "períodoHistórico" in m:
        periodo_uri = criar_periodo(g, m["períodoHistórico"])
        g.add((mestre_uri, SAPIENTA.viveuEm, periodo_uri))

    for disc in m.get("disciplinas", []):
        disc_uri = criar_disciplina(g, disc)
        g.add((mestre_uri, SAPIENTA.ensina, disc_uri))

# === Povoa obras ===
for o in obras:
    obra_uri = criar_obra(g, o["titulo"])
    autor_uri = criar_mestre(g, o["autor"])
    g.add((obra_uri, SAPIENTA.foiEscritoPor, autor_uri))
    for conceito in o.get("conceitos", []):
        conc_uri = conceito_map.get(conceito) or criar_conceito(g, conceito)
        g.add((obra_uri, SAPIENTA.explica, conc_uri))

# === Povoa aprendizes ===
for a in aprendizes:
    idade = a.get("idade")
    aprendiz_uri = criar_aprendiz(g, a["nome"], idade=idade)
    for disc in a.get("disciplinas", []):
        disc_uri = criar_disciplina(g, disc)
        g.add((aprendiz_uri, SAPIENTA.aprende, disc_uri))
        
# === Guardar ontologia atualizada ===
g.serialize(destination=OUTPUT_FILE, format="ttl")
print(f"Ontologia povoada guardada em '{OUTPUT_FILE}'")
