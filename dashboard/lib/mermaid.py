"""Render Mermaid diagrams in Streamlit via components.html."""
import streamlit.components.v1 as components


def render_mermaid(diagram: str, height: int = 400) -> None:
    """Render a Mermaid diagram inside an HTML component.

    The .mermaid div is hidden until Mermaid JS processes it,
    preventing raw code from flashing on screen.
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background: white; }}
            .mermaid {{ visibility: hidden; }}
            .mermaid[data-processed="true"] {{ visibility: visible; }}
        </style>
    </head>
    <body>
        <div class="mermaid">
{diagram}
        </div>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'default',
                securityLevel: 'loose',
            }});
            // Ensure visibility after render
            mermaid.run().then(function() {{
                document.querySelectorAll('.mermaid').forEach(function(el) {{
                    el.setAttribute('data-processed', 'true');
                }});
            }});
        </script>
    </body>
    </html>
    """
    components.html(html, height=height)
