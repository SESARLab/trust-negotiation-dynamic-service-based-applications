import json
from pathlib import Path


def export_dynamic_snapshot(
        events: list[dict],
        output_dir: Path
) -> None:
    with open(output_dir / 'dynamic.json', 'w', encoding='utf-8') as fp:
        json.dump({'events': events}, fp, indent=2)
