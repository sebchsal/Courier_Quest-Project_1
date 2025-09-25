import os
import glob

MAX_VERSIONS = 1

def clean_old_versions(base_dir, base_filename, max_versions=MAX_VERSIONS):
    """Conserva solo las últimas max_versions versiones de un JSON"""
    pattern = os.path.join(base_dir, f"{base_filename}_*")
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)

    removed = []
    if len(files) > max_versions:
        for old_file in files[max_versions:]:
            try:
                os.remove(old_file)
                removed.append(os.path.basename(old_file))
            except Exception as e:
                removed.append(f"{os.path.basename(old_file)} (error: {e})")
    return removed

def clean_all():
    """Limpia versiones viejas en /data y /api_cache y devuelve resumen"""
    summary = {}
    for base_dir, files in {
        "data": ["ciudad.json", "pedidos.json", "weather.json"],
        "api_cache": ["map.json", "jobs.json", "weather.json"]
    }.items():
        if not os.path.exists(base_dir):
            continue
        for filename in files:
            removed = clean_old_versions(base_dir, filename, MAX_VERSIONS)
            if removed:
                summary[f"{base_dir}/{filename}"] = removed
    return summary