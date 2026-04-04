"""Render Mermaid diagrams in Streamlit via components.html."""
import hashlib
import streamlit.components.v1 as components


def render_mermaid(diagram: str, height: int = 400) -> None:
    """Render a Mermaid diagram inside an HTML component.

    Uses a unique ID per diagram and a template script tag to avoid
    HTML entity issues with special characters in diagram syntax.
    """
    # Unique ID to avoid conflicts when multiple diagrams on same page
    uid = "m" + hashlib.md5(diagram.encode()).hexdigest()[:8]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 8px; background: white; font-family: sans-serif; }}
            #output-{uid} {{ min-height: 50px; }}
            .error {{ color: red; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div id="output-{uid}"></div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: false, theme: 'default', securityLevel: 'loose' }});
            const diagram = `{diagram}`;
            try {{
                const {{ svg }} = await mermaid.render('{uid}', diagram);
                document.getElementById('output-{uid}').innerHTML = svg;
            }} catch(e) {{
                document.getElementById('output-{uid}').innerHTML = '<p class="error">Diagram error: ' + e.message + '</p>';
            }}
        </script>
    </body>
    </html>
    """
    components.html(html, height=height)
