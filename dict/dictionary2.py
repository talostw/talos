#!/usr/bin/env python3
import sys
from string import Template
import operator
import csv
from datetime import datetime
import cgi

class Dictionary:
    """ Dictionary mapping to generate a XDXF formatted dictionary """
    title = "Unnamed Dictionary"
    full_title = "Unnamed Dictionary"
    description = "No description"
    file_ver = "001"
    creation_date = datetime.utcnow().strftime("%Y-%m-%d")
    langs = {"from": "ENG", "to": "ENG"}
    lexi = {}
    template = Template('''\
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE xdxf SYSTEM "https://raw.github.com/soshial/xdxf_makedict/master/format_standard/xdxf_strict.dtd">
<xdxf lang_from="$lang_from" lang_to="$lang_to" format="logical" revision="032beta">
    <meta_info>
        <title>$title</title>
        <full_title>$fulltitle</full_title>
        <description>$description</description>
        <file_ver>$file_ver</file_ver>
        <creation_date>$creation_date</creation_date>
    </meta_info>
    <lexicon>
$payload
    </lexicon>
</xdxf>
''')
    template_article = Template("\t\t<ar>\n\t\t\t<k>$word_enc</k> <!-- $word -->\n$payload\n\t\t</ar>\n")
    template_def = Template("\t\t\t<def>\n\t\t\t\t$definition\t\t\t</def>")
    template_ex = Template("\t\t\t\t<ex>\n\t\t\t\t\t<ex_orig>$ex_orig</ex_orig>\n\t\t\t\t\t<ex_tran>$ex_tran</ex_tran>\n\t\t\t\t</ex>\n")

    def set_title(self, title):
        self.title = title

    def set_full_title(self, title):
        self.full_title = title

    def set_description(self, description):
        self.description = description

    def set_file_ver(self, file_ver):
        self.file_ver = file_ver

    def set_creation_date(self, creation_date):
        self.creation_date = creation_date

    def set_langs(self, frm, to):
        self.langs = {"from": frm, "to": to}

    def add(self, word, defi, exam = None):
        arti = self.lexi.get(word)
        if arti == None:
            self.lexi[word] = []
            arti = self.lexi.get(word)

        d = {}
        d["def"] = defi
        if exam != None:
            d["exam"] = exam
        else:
            d["exam"] = []

        arti.append(d)

    def generate(self):
        lexicon = ""
        sorted_lexi = sorted(self.lexi.items(), key=operator.itemgetter(0))

        lexicon_payload = ""
        for word, defs in sorted_lexi:
            word_enc=cgi.escape(word).encode('ascii', 'xmlcharrefreplace')
            word_enc=word_enc.decode()
            payload = ""
            for defi in defs:
                e = "".join(map(lambda a: self.template_ex.substitute(ex_orig=a[0], ex_tran=a[1]), defi["exam"]))
                d = self.template_def.substitute(definition="<deftext>"+defi["def"]+"</deftext>\n"+e)
                payload += d

            if len(defs) > 1:
                payload = self.template_def.substitute(definition=payload)

            article = self.template_article.substitute(word=word, word_enc=word_enc, payload=payload)
            lexicon_payload += article

        return self.template.substitute(
                lang_from=self.langs["from"],
                lang_to=self.langs["to"],
                title=self.title,
                fulltitle=self.full_title,
                description=self.description,
                file_ver=self.file_ver,
                creation_date=self.creation_date,
                payload=lexicon_payload)

if __name__ == "__main__":
    with open(sys.argv[2]) as dictfile, open(sys.argv[3]) as exfile:

        examples = {}
        for item in csv.reader(exfile):
            try:
                sid = int(item[0])
            except ValueError:
                continue
            examples[sid] = (item[4], item[3])

        tayal = Dictionary()
        tayal.set_title("Chinese - Atayal ("+sys.argv[1]+")")
        tayal.set_full_title("Chinese to Atayal ("+sys.argv[1]+") to Dictionary")
        tayal.set_langs("ZHT", "TAY")

        for item in csv.reader(dictfile):
            try:
                sid = int(item[0])
            except ValueError:
                continue

            word = item[4].strip()
            definition = item[3]
            if item[5] != "":
                example = map(lambda x: examples[int(x)], item[5].split(";"))
            elif item[6] != "":
                example = map(lambda x: examples[int(x)], item[6].split(";"))
            else:
                example = None
            tayal.add(word, definition, example)

        print(tayal.generate())
