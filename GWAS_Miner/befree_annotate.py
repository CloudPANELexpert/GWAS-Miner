import html
import re
from datetime import datetime
from difflib import SequenceMatcher

from GWAS_Miner import BioC
from GWAS_Miner.BioC import BioCLocation, BioCAnnotation
from Utility_Functions import Utility

def get_befree_data(pmid):
    befree_data = {}
    headers_skipped = False
    # retrieve befree variants
    with open("vdas_version_2_mesh.tsv", "r", encoding="utf-8") as f_in:
        for line in f_in.readlines():
            if not headers_skipped:
                headers_skipped = not headers_skipped
                continue
            line = line.split("\t")
            if line[0] != pmid:
                continue
            if line[0] not in befree_data.keys():
                befree_data[line[0]] = []
            befree_data[line[0]].append({"sentence_number": line[3], "variantid": line[4], "variant_offset": line[6],
                                         "diseaseid": line[7], "disease_text": line[8], "disease_offset": line[9],
                                         "sentence": html.unescape(line[10].lstrip('"').rstrip('"')),
                                         "meshid": line[11],
                                         "mapping_source": line[13]})
    # retrieve befree genes
    with open("gdas_version_1_mesh.tsv", "r", encoding="utf-8") as f_in:
        for line in f_in.readlines():
            if not headers_skipped:
                headers_skipped = not headers_skipped
                continue
            line = line.split("\t")
            if line[0] != pmid:
                continue
            if line[0] not in befree_data.keys():
                befree_data[line[0]] = []
            befree_data[line[0]].append({"sentence_number": line[3], "ncbi_id": line[4], "gene_offset": line[6],
                                         "gene_text": line[5],
                                         "diseaseid": line[7], "disease_text": line[8], "disease_offset": line[9],
                                         "sentence": html.unescape(line[10].lstrip('"').rstrip('"')),
                                         "meshid": line[11],
                                         "mapping_source": line[13]})
    return befree_data


def get_bioc_annotations(annotations, offset, nlp):
    current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    for annot in annotations:
        loc = BioCLocation(offset=annot["offset"] + offset, length=annot["length"])
        if "RSID" not in annot["entity_type"] and "PVAL" not in annot["entity_type"] \
                and "GENE" not in annot["entity_type"]:
            genomic_trait = BioCAnnotation(id=F"T{nlp.t}", infons={"type": "trait", "identifier": F"MeSH:{annot['id']}",
                                                                   "annotator": "BeFree@example.com",
                                                                   "updated_at": current_datetime},
                                           locations=[loc], text=annot["text"])
            nlp.annotations.append(genomic_trait)
            nlp.t += 1
        elif "RSID" in annot["entity_type"]:
            marker_identifier = BioCAnnotation(id=F"V{nlp.v}",
                                               infons={"type": "genetic_variant", "identifier": F"dbSNP:{annot['text']}",
                                                       "annotator": "BeFree@example.com",
                                                       "updated_at": current_datetime},
                                               locations=[loc], text=annot["text"])
            nlp.annotations.append(marker_identifier)
            nlp.v += 1
        elif "PVAL" in annot["entity_type"]:
            p_value = BioCAnnotation(id=F"P{nlp.p}", infons={"type": "significance", "identifier": annot["id"],
                                                             "annotator": "BeFree@example.com",
                                                             "updated_at": current_datetime},
                                     locations=[loc], text=annot["text"])
            nlp.annotations.append(p_value)
            nlp.p += 1
        elif "GENE" in annot["entity_type"]:
            gene = BioCAnnotation(id=F"G{nlp.g}", infons={"type": "gene", "identifier": F"Entrez:{annot['id']}",
                                                      "annotator": "BeFree@example.com",
                                                      "updated_at": current_datetime},
                                  locations=[loc], text=annot["text"])
            nlp.annotations.append(gene)
            nlp.g += 1
    return nlp


def get_closest_index(text, search, target):
    closest_index = None
    closest_difference = None
    for match in re.finditer(search, text, flags=re.MULTILINE):
        if closest_index is None:
            closest_index = match.start()
            closest_difference = abs(target - closest_index)
        elif closest_difference and abs(target - match.start()) < closest_difference:
            closest_index = match.start()
            closest_difference = abs(target - closest_index)
    return closest_index


def get_befree_annotations(study, nlp, current_datetime):
    pmid = study["documents"][0]["passages"][0]["infons"]["article-id_pmid"]
    befree_data = get_befree_data(pmid)
    if pmid in befree_data.keys():
        study_befree_data = befree_data[pmid]
        relations = []
        contains_missing_entities = False
        for passage in study['documents'][0]['passages']:
            annotations = []
            if passage['infons']['section_type'] == "ABSTRACT" and "title" not in passage['infons']['type']:
                text = passage["text"]
                for entry in study_befree_data:
                    disease_node_id = nlp.t
                    marker_node_id = nlp.v
                    gene_node_id = nlp.g
                    is_gene = "ncbi_id" in entry.keys()
                    sent = sorted([(SequenceMatcher(None, x, entry['sentence']).ratio(), x) for x in text.split(". ")],
                                  key=lambda y: y[0], reverse=True)[0]
                    sent_score = sent[0]
                    sent = sent[1]
                    if not sent or sent_score < 0.7:
                        continue
                    sentence_offset = text.index(sent) + passage["offset"]
                    try:
                        loc = BioC.BioCLocation(offset=get_closest_index(sent, entry["disease_text"], int(
                            entry["disease_offset"][:entry["disease_offset"].index("#")]) + sentence_offset) + sentence_offset,
                                                length=len(entry["disease_text"]))
                        annotations.append(BioC.BioCAnnotation(id=F"T{nlp.t}",
                                                               infons={"type": "trait",
                                                                       "identifier": F"MeSH:{entry['meshid']}",
                                                                       "annotator": "GWASMiner@le.ac.uk",
                                                                       "updated_at": current_datetime},
                                                               locations=[loc], text=entry["disease_text"]))
                        nlp.t += 1
                        if not is_gene:
                            loc = BioC.BioCLocation(offset=get_closest_index(sent, entry["variantid"], int(
                                    entry["variant_offset"][:entry["variant_offset"].index("#")]) + sentence_offset) + sentence_offset,
                                                    length=len(entry["variantid"]))
                            annotations.append(BioC.BioCAnnotation(id=F"V{nlp.v}",
                                                infons={"type": "genetic_variant", "identifier": F"dbSNP:{entry['variantid']}",
                                                        "annotator": "GWASMiner@le.ac.uk",
                                                        "updated_at": current_datetime},
                                                locations=[loc], text=entry["variantid"]))
                            nlp.v += 1
                        else:
                            loc = BioC.BioCLocation(offset=get_closest_index(sent, entry["gene_text"], int(
                                    entry["gene_offset"][:entry["gene_offset"].index("#")]) + sentence_offset) + sentence_offset,
                                                    length=len(entry["gene_text"]))
                            annotations.append(BioC.BioCAnnotation(id=F"G{nlp.g}",
                                                infons={"type": "gene", "identifier": F"Entrez:{entry['ncbi_id']}",
                                                        "annotator": "GWASMiner@le.ac.uk",
                                                        "updated_at": current_datetime},
                                                locations=[loc], text=entry["gene_text"]))
                            nlp.g += 1
                    except TypeError as te:
                        contains_missing_entities = True
                        continue
                    if contains_missing_entities:
                        print(F"PMID: {pmid} - contains missing entities from sentences.")
                    # nlp = get_bioc_annotations(annotations, passage["offset"], nlp)
                    phenotype_node = BioC.BioCNode(refid=F"T{disease_node_id}", role="")
                    marker_node = BioC.BioCNode(refid=F"M{marker_node_id}", role="")
                    gene_node = BioC.BioCNode(refid=F"G{gene_node_id}", role="")
                    bioc_relation = BioC.BioCRelation(id=F"R{nlp.r}",
                                                      infons={"type": "Gene_Trait" if is_gene else "GeneticVariant_Trait",
                                                              "annotator": "tr142@le.ac.uk",
                                                              "updated_at": datetime.now().strftime(
                                                                  "%Y-%m-%dT%H:%M:%SZ")},
                                                      nodes=[phenotype_node, marker_node] if not is_gene else [
                                                          phenotype_node, gene_node])
                    nlp.r += 1
                    relations.append(bioc_relation)
                for annot in annotations:
                    passage['annotations'].append(annot)
        if relations:
            relations = Utility.remove_duplicate_bioc_associations(relations)
            for relation in relations:
                study['documents'][0]['relations'].append(relation)
    return study, nlp
