"""Generate SVG diagrams for state machines."""
import logging

logger = logging.getLogger(__name__)


def generate_state_machine_svg(state_machines: list) -> str:
    """Generate an SVG diagram showing all state machines.

    Args:
        state_machines: list of state machine dicts with entity, states, transitions.

    Returns:
        SVG string.
    """
    if not state_machines:
        return "<svg xmlns='http://www.w3.org/2000/svg'><text x='10' y='20'>No state machines</text></svg>"

    # Layout: each state machine in a horizontal row
    machines = state_machines if isinstance(state_machines, list) else state_machines.get("state_machines", [])

    if not machines:
        return "<svg xmlns='http://www.w3.org/2000/svg'><text x='10' y='20'>No state machines</text></svg>"

    # Calculate dimensions
    max_states = max(len(sm.get("states", [])) for sm in machines)
    num_machines = len(machines)
    state_radius = 28
    state_gap = 100
    row_height = 140
    width = max(600, max_states * state_gap + 60)
    height = num_machines * row_height + 40

    colors = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"]

    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {width} {height}' font-family='system-ui, sans-serif'>",
        f"<rect width='{width}' height='{height}' fill='#0a0a0a'/>",
    ]

    for i, sm in enumerate(machines):
        entity = sm.get("entity", "Unknown")
        states = sm.get("states", [])
        transitions = sm.get("transitions", [])
        initial = sm.get("initial_state", states[0] if states else "")

        y_base = i * row_height + 20

        # Entity label
        color = colors[i % len(colors)]
        parts.append(f"<text x='15' y='{y_base + 5}' fill='{color}' font-size='12' font-weight='700'>{entity}</text>")

        # State positions
        state_positions = {}
        for j, state in enumerate(states):
            x = 80 + j * state_gap
            y = y_base + 40
            state_positions[state] = (x, y)

            # State circle
            is_initial = state == initial
            stroke = color if is_initial else "#444"
            sw = 2 if is_initial else 1.5
            parts.append(f"<circle cx='{x}' cy='{y}' r='{state_radius}' fill='#181818' stroke='{stroke}' stroke-width='{sw}'/>")
            parts.append(f"<text x='{x}' y='{y + 4}' text-anchor='middle' fill='#e8e8e8' font-size='9'>{state}</text>")

        # Transitions (arrows)
        for t in transitions:
            from_state = t.get("from_state", "")
            to_state = t.get("to_state", "")
            if from_state not in state_positions or to_state not in state_positions:
                continue

            x1, y1 = state_positions[from_state]
            x2, y2 = state_positions[to_state]

            if from_state == to_state:
                # Self-loop
                parts.append(f"<path d='M {x1-15} {y1-20} A 25 25 0 1 1 {x1+15} {y1-20}' fill='none' stroke='#555' stroke-width='1' marker-end='url(#arrowhead)'/>")
            else:
                # Line between states
                dx = x2 - x1
                dy = y2 - y1
                length = (dx * dx + dy * dy) ** 0.5
                if length == 0:
                    continue
                # Shorten line to not overlap circles
                nx, ny = dx / length, dy / length
                sx = x1 + nx * state_radius
                sy = y1 + ny * state_radius
                ex = x2 - nx * state_radius
                ey = y2 - ny * state_radius

                parts.append(f"<line x1='{sx}' y1='{sy}' x2='{ex}' y2='{ey}' stroke='#555' stroke-width='1.2' marker-end='url(#arrowhead)'/>")

                # Trigger label at midpoint
                mx, my = (sx + ex) / 2, (sy + ey) / 2 - 5
                trigger = t.get("trigger", "")[:20]
                parts.append(f"<text x='{mx}' y='{my}' text-anchor='middle' fill='#888' font-size='7'>{trigger}</text>")

    # Arrowhead marker
    parts.append("""<defs><marker id='arrowhead' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='5' markerHeight='5' orient='auto'>
        <path d='M 0 0 L 10 5 L 0 10 z' fill='#555'/>
    </marker></defs>""")

    parts.append("</svg>")
    return "\n".join(parts)