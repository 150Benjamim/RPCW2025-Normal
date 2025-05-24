from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, OWL, RDFS

# Arquivo da ontologia existente e onde será salva
TTL_FILE = "sapientia_ind.ttl"
OUTPUT_FILE = "sapientia_ind.ttl"

# Namespaces
SAPIENTA = Namespace("http://example.org/sapienta#")

# Carregar grafo
g = Graph()
g.parse(TTL_FILE, format="ttl")
g.bind("", SAPIENTA)

# Assegurar que a propriedade :estudaCom está definida corretamente
estudaCom = SAPIENTA.estudaCom
g.add((estudaCom, RDF.type, OWL.ObjectProperty))
g.add((estudaCom, URIRef("http://www.w3.org/2000/01/rdf-schema#domain"), SAPIENTA.Aprendiz))
g.add((estudaCom, URIRef("http://www.w3.org/2000/01/rdf-schema#range"), SAPIENTA.Mestre))

# Query INSERT para inferir a relação estudaCom
# Se um aprendiz aprende uma disciplina, e um mestre ensina essa mesma disciplina,
# então o aprendiz estudaCom o mestre.
insert_query = """
PREFIX : <http://example.org/sapienta#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

INSERT {
  ?aprendiz :estudaCom ?mestre .
}
WHERE {
  ?aprendiz rdf:type :Aprendiz .
  ?aprendiz :aprende ?disc .
  ?mestre rdf:type :Mestre .
  ?mestre :ensina ?disc .
}
"""

# Executar a query no grafo
g.update(insert_query)

# Guardar ontologia com os novos triplos inferidos
g.serialize(destination=OUTPUT_FILE, format="ttl")
print(f"Inferência concluída. Ontologia atualizada em '{OUTPUT_FILE}'")



# Criar a nova propriedade :daBasesPara (disciplina → aplicação)
daBasesPara = SAPIENTA.daBasesPara
g.add((daBasesPara, RDF.type, OWL.ObjectProperty))
g.add((daBasesPara, RDFS.domain, SAPIENTA.Disciplina))
g.add((daBasesPara, RDFS.range, SAPIENTA.Aplicacao))

# Query INSERT (inferência baseada nos conceitos em comum)
# Se uma disciplina estuda um conceito que tem uma aplicação X,
# então essa disciplina dáBasesPara X.
insert_query = """
PREFIX : <http://example.org/sapienta#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

INSERT {
  ?disciplina :daBasesPara ?aplicacao .
}
WHERE {
  ?disciplina rdf:type :Disciplina .
  ?disciplina :estuda ?conceito .
  ?conceito :temAplicacaoEm ?aplicacao .
}
"""

# Executar a query
g.update(insert_query)

# Guardar grafo atualizado
g.serialize(destination=OUTPUT_FILE, format="ttl")
print(f"Inferência concluída. Ontologia atualizada com ':daBasesPara' em '{OUTPUT_FILE}'")