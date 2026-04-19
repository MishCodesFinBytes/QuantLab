"""Blue digital-globe aesthetic constants.

Colour palette: dark navy background + glowing cyan continent outlines +
city node dots. Inspired by satellite-tech / network-topology imagery.
All colours are plain Python lists so they can be used as pydeck layer
arguments without importing pydeck.
"""

# Deck background ─────────────────────────────────────────────────────────────
# Deep navy — reads as "space" or "deep ocean" while keeping enough contrast
# for cyan continent glows to pop.  Value is normalised float RGBA for
# deck.gl's clearColor parameter.
CLEAR_COLOR: list[float] = [1.0, 1.0, 1.0, 1.0]   # white outside sphere

# Continent fills & borders ───────────────────────────────────────────────────
CONTINENT_FILL:       list[int] = [20, 40, 80, 60]       # translucent navy land
CONTINENT_STROKE:     list[int] = [0, 200, 220, 180]     # glowing cyan border
CONTINENT_LINE_WIDTH: float = 1.5                         # pixels

# City / destination node dots ────────────────────────────────────────────────
CITY_NODE_COLOR:  list[int] = [0, 200, 220, 220]   # bright cyan glow
CITY_NODE_RADIUS: int = 80_000                      # metres

# Arc defaults ────────────────────────────────────────────────────────────────
ARC_DEFAULT_COLOR: tuple[int, int, int] = (0, 180, 220)  # cyan

# Epicenter highlight ─────────────────────────────────────────────────────────
EPICENTER_FILL:   list[int] = [200, 30, 30, 90]
EPICENTER_STROKE: list[int] = [255, 160, 160, 200]

# Sequential ramp anchors — for pollution / quality indexes ───────────────────
# 0 = clean (green), 1 = worst (red). Muted so strong signals don't overwhelm
# the blue globe palette.
QUALITY_CLEAN: tuple[int, int, int] = (50, 160, 80)    # muted sage
QUALITY_WORST: tuple[int, int, int] = (180, 50, 50)    # muted rose
