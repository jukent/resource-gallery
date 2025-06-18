import sys
import json
import urllib.request
import yaml
import concurrent.futures

from unist import *

LAYOUT_STYLE = {
    "display": "inline-block",
    "borderRadius": 8,
    "color": "white",
    "padding": 5,
    "margin": 5,
}

DEFAULT_STYLE = {"background": "#4E66F6", **LAYOUT_STYLE}

styles = {
    "domains": {"background": "#7A77B4", **LAYOUT_STYLE},
    "packages": {"background": "#B83BC0", **LAYOUT_STYLE},
}


def fetch_yaml(url: str):
    with urllib.request.urlopen(url) as response:
        body = response.read().decode()
    return yaml.load(body, yaml.SafeLoader)


def render_resource(resource: dict):

    title = resource["title"]
    resource_url = resource["url"]
    description = resource["description"]


    #if "thumbnail" in resource:
    #else:
    try:
        thumbnail = "https://projectpythia.org/resource-gallery/" + resource['thumbnail']
    except:
        thumbnail = "https://projectpythia.org/_static/thumbnails/ProjectPythia_Blue.png"

    # Build tags
    tags = resource["tags"]

    return {
        "type": "card",
        "url": resource_url,
        "children": [
            {"type": "cardTitle", "children": [text(title)]},
            div([
                image(thumbnail),
                text(description),
                div(
                        [
                            span(
                                [text(item)],
                                style=styles.get(name, DEFAULT_STYLE),
                            )
                            for name, items in tags.items()
                            if items is not None
                            for item in items
                        ]
                )
            ])
        ]
    }

    return {
        "type": "card",
        "url": resource_url,
        "children": [
            {"type": "cardTitle", "children": [text(title)]},
            div(
                [
                    description,
                    div(
                        [
                            span(
                                [text(item)],
                                style=styles.get(name, DEFAULT_STYLE),
                            )
                            for name, items in tags.items()
                            if items is not None
                            for item in items
                        ]
                    ),
                ],
            ),
        ],
    }


def render_resources(pool):
    
    resources = fetch_yaml("https://raw.githubusercontent.com/ProjectPythia/resource-gallery/main/portal/resource_gallery.yaml")

    return [*pool.map(render_resource, resources)]


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor() as pool:
        # Parse the AST as JSON on stdin
        data = sys.stdin.read()
        ast = json.loads(data)

        # Find our resource nodes in the AST
        resource_nodes = find_all_by_type(ast, "pythia-resources")

        # In-place mutate the AST to replace resource nodes with card grids
        children = render_resources(pool)

        # Mutate our resource nodes in-place
        for node in resource_nodes:
            node.clear()
            node.update(grid([1, 1, 2, 3], children))
            node["children"] = children

        # Write back to stdout!
        print(json.dumps(ast))
