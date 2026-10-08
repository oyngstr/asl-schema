"""Build schema.json from src/. Run after any edit:  python build.py

schema.json maps each asl1.com path to its canonical URL and JSON-LD graph.
The site header loads it (loader.js) and injects both into the page.
Fails loudly on anything malformed so a bad edit never goes live.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://asl1.com"


def load(name):
    with open(os.path.join(HERE, "src", name)) as f:
        return json.load(f)


def city(name):
    return {"@type": "City", "name": name,
            "containedInPlace": {"@type": "State", "name": "Utah"}}


def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p}
        for i, (n, p) in enumerate(items)]}


def build():
    biz = load("business.json")
    pages = load("pages.json")
    priority = biz.pop("priorityCities")
    business = biz
    ref = {"@id": business["@id"]}
    out = {}

    def add(path, nodes):
        if path in out:
            sys.exit(f"duplicate path {path}")
        out[path] = {
            "canonical": None if path in pages["no_canonical"] else SITE + path,
            "jsonld": {"@context": "https://schema.org", "@graph": [copy.deepcopy(business)] + nodes},
        }

    for s in pages["services"]:
        node = {
            "@type": "Service",
            "@id": SITE + s["path"] + "#service",
            "name": s["name"],
            "serviceType": s["serviceType"],
            "url": SITE + s["path"],
            "provider": ref,
            "areaServed": [city(c) for c in priority] if s.get("priority") else {"@type": "State", "name": "Utah"},
        }
        nodes = [node, crumbs([("Home", "/"), ("Services", "/services"), (s["name"], s["path"])])]
        faq = [x for x in pages["faqs"].get(s["path"], []) if x.get("q") and x.get("a")]
        if faq:
            nodes.append({"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": x["q"],
                 "acceptedAnswer": {"@type": "Answer", "text": x["a"]}} for x in faq]})
        add(s["path"], nodes)

    for b in pages["blog_posts"]:
        add(b["path"], [
            {"@type": "BlogPosting", "headline": b["headline"], "url": SITE + b["path"],
             "datePublished": b["datePublished"], "author": ref, "publisher": ref,
             "mainEntityOfPage": SITE + b["path"]},
            crumbs([("Home", "/"), ("Blog", "/blog"), (b["headline"], b["path"])]),
        ])

    for p in pages["projects"]:
        node = {"@type": "CreativeWork", "name": p["name"], "url": SITE + p["path"],
                "creator": ref, "about": "Landscape design and build project"}
        if p.get("city"):
            node["locationCreated"] = city(p["city"])
        add(p["path"], [node, crumbs([("Home", "/"), ("Projects", "/projects"), (p["name"], p["path"])])])

    for o in pages["other_pages"]:
        trail = [("Home", "/")]
        if o.get("parent"):
            parent = next(x for x in pages["other_pages"] if x["path"] == o["parent"])
            trail.append((parent["name"], parent["path"]))
        trail.append((o["name"], o["path"]))
        add(o["path"], [crumbs(trail)])

    for path in pages["no_canonical"]:
        out.setdefault(path, {"canonical": None, "jsonld": None})

    result = {"site": SITE, "pages": out}
    text = json.dumps(result, indent=1, ensure_ascii=False)
    json.loads(text)
    with open(os.path.join(HERE, "schema.json"), "w") as f:
        f.write(text + "\n")
    print(f"schema.json: {len(out)} pages")
    return result


if __name__ == "__main__":
    build()
