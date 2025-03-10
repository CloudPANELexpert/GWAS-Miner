#!/usr/bin/env python

# This file was taken from the following public repository: https://github.com/ncbi-nlp/BioC-JSON
#

#### Write a BioC collection in JSON
import json

import bioc


class BioC2JSON:
    def node(self, node):
        json_node = {'refid': node.refid, 'role': node.role}
        return json_node

    def relation(self, rel):
        json_rel = {}
        json_rel['id'] = rel.id
        json_rel['infons'] = rel.infons
        json_rel['nodes'] = [self.node(n) for n in rel.nodes]
        return json_rel

    def location(self, loc):
        json_loc = {'offset': int(loc.offset), 'length': int(loc.length)}
        return json_loc

    def annotation(self, note):
        json_note = {}
        json_note['id'] = note.id
        json_note['infons'] = note.infons
        json_note['text'] = note.text
        json_note['locations'] = [self.location(l)
                                  for l in note.locations]
        return json_note

    def sentence(self, sent):
        json_sent = {}
        json_sent['infons'] = sent.infons
        json_sent['offset'] = int(sent.offset)
        json_sent['text'] = sent.text
        json_sent['annotations'] = [self.annotation(a)
                                    for a in sent.annotations]
        json_sent['relations'] = [self.relation(r)
                                  for r in sent.relations]
        return json_sent

    def passage(self, psg):
        json_psg = {}
        json_psg['infons'] = psg.infons
        json_psg['offset'] = int(psg.offset)
        json_psg['text'] = psg.text
        json_psg['text'] = psg.text if psg.text else ""
        json_psg['sentences'] = [self.sentence(s)
                                 for s in psg.sentences]
        json_psg['annotations'] = [self.annotation(a)
                                   for a in psg.annotations]
        json_psg['relations'] = [self.relation(r)
                                 for r in psg.relations]
        return json_psg

    def document(self, doc):
        json_doc = {}
        json_doc['id'] = doc.id
        json_doc['infons'] = doc.infons
        json_doc['passages'] = [self.passage(p)
                                for p in doc.passages]
        json_doc['relations'] = [self.relation(r)
                                 for r in doc.relations]
        return json_doc

    def collection(self, collection):
        json_collection = {}
        json_collection['source'] = collection.source
        json_collection['date'] = collection.date
        json_collection['key'] = collection.key
        json_collection['infons'] = collection.infons
        json_collection['documents'] = [self.document(d)
                                        for d in collection.documents]
        return json_collection


class JSON2BioC:

    def node(self, json_node):
        node = bioc.BioCNode()
        node.refid = json_node['refid']
        node.role = json_node['role']
        return node

    def relation(self, json_rel):
        rel = bioc.BioCRelation()
        rel.id = json_rel['id']
        rel.infons = json_rel['infons']
        rel.nodes = [self.node(n) for n in json_rel['nodes']]
        return rel

    def location(self, json_loc):
        loc = bioc.BioCLocation()
        loc.offset = str(json_loc['offset'])
        loc.length = str(json_loc['length'])
        return loc

    def annotation(self, json_note):
        note = bioc.BioCAnnotation()
        note.id = json_note['id']
        note.infons = json_note['infons']
        note.text = json_note['text']
        note.locations = [self.location(l)
                          for l in json_note['locations']]
        return note

    def sentence(self, json_sent):
        sent = bioc.BioCSentence()
        sent.infons = json_sent['infons']
        sent.offset = str(json_sent['offset'])
        sent.text = json_sent['text']
        sent.annotations = [self.annotation(a)
                            for a in json_sent['annotations']]
        sent.relations = [self.relation(r)
                          for r in json_sent['relations']]
        return sent

    def passage(self, json_psg):
        psg = bioc.BioCPassage()
        psg.infons = json_psg['infons']
        psg.offset = str(json_psg['offset'])
        psg.text = json_psg.get('text')
        psg.sentences = [self.sentence(s)
                         for s in json_psg['sentences']]
        psg.annotations = [self.annotation(a)
                           for a in json_psg['annotations']]
        psg.relations = [self.relation(r)
                         for r in json_psg['relations']]
        return psg

    def document(self, json_doc):
        doc = bioc.BioCDocument()
        doc.id = json_doc['id']
        doc.infons = json_doc['infons']
        doc.passages = [self.passage(p)
                        for p in json_doc['passages']]
        doc.relations = [self.relation(r)
                         for r in json_doc['relations']]
        return doc

    def collection(self, json_collection):
        collection = bioc.BioCCollection()
        collection.source = json_collection['source']
        collection.date = json_collection['date']
        collection.key = json_collection['key']
        collection.infons = json_collection['infons']
        collection.documents = [self.document(d)
                                for d in json_collection['documents']]
        return collection


def output_xml(in_file, out_file):
    bioc_json = None
    bioc_json = json.loads(in_file)

    json2bioc = JSON2BioC()
    bioc_collection = json2bioc.collection(bioc_json)

    writer = bioc.BioCXMLWriter(out_file, bioc_collection)
    writer.write()


def convert_xml_to_json(in_file, out_file):
    reader = bioc.BioCXMLReader(in_file)
    reader.read()

    bioc2json = BioC2JSON()
    bioc_json = bioc2json.collection(reader.collection)
    with open(out_file, 'w') as f:
        json.dump(bioc_json, f, indent=2)
        print(file=f)
