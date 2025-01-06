import subprocess
import json
from collections import defaultdict

def get_leaf_packages():
    try:
        result = subprocess.run(['brew', 'leaves'], capture_output=True, text=True, check=True)
        formulas = result.stdout.splitlines()
        return formulas
    except subprocess.CalledProcessError as e:
        print("Fehler beim Abrufen der Leaf-Pakete (Formulas):", e)
        return []

def get_installed_casks():
    try:
        result = subprocess.run(['brew', 'list', '--cask'], capture_output=True, text=True, check=True)
        casks = result.stdout.splitlines()
        return casks
    except subprocess.CalledProcessError as e:
        print("Fehler beim Abrufen der installierten Casks:", e)
        return []

def get_formula_info(package_name):
    try:
        result = subprocess.run(['brew', 'info', '--json=v2', package_name], capture_output=True, text=True, check=True)
        package_info = json.loads(result.stdout)
        if 'formulae' in package_info and package_info['formulae']:
            return package_info['formulae'][0]
        else:
            return None
    except subprocess.CalledProcessError:
        return None
    except json.JSONDecodeError:
        return None

def get_cask_info(cask_name):
    try:
        result = subprocess.run(['brew', 'info', '--json=v2', '--cask', cask_name], capture_output=True, text=True, check=True)
        package_info = json.loads(result.stdout)
        if 'casks' in package_info and package_info['casks']:
            return package_info['casks'][0]
        else:
            return None
    except subprocess.CalledProcessError:
        return None
    except json.JSONDecodeError:
        return None

def group_packages_by_license(packages):
    license_packages = defaultdict(list)
    for package in packages:
        if not package:
            continue  # Überspringe Pakete ohne Daten
        license_type = package.get('license', 'Unknown') or 'Unknown'
        package_name = package.get('name', 'Unknown')
        if isinstance(package_name, list):  # Falls es eine Liste ist
            package_name = package_name[0]
        license_packages[license_type].append(package_name)
    return dict(sorted(license_packages.items(), key=lambda x: (x[0] or 'Unknown')))

def main():
    leaf_formulas = get_leaf_packages()
    installed_casks = get_installed_casks()

    if not leaf_formulas and not installed_casks:
        print("Keine Leaf-Pakete oder Casks gefunden.")
        return

    packages_info = []

    for formula in leaf_formulas:
        info = get_formula_info(formula)
        if info:
            packages_info.append(info)

    for cask in installed_casks:
        info = get_cask_info(cask)
        if info:
            packages_info.append(info)

    grouped_by_license = group_packages_by_license(packages_info)

    for license_type, packages in grouped_by_license.items():
        print(f"License: {license_type}")
        for package in sorted(packages):  # Alphabetische Sortierung
            print(f"  - {package}")
        print()

if __name__ == "__main__":
    main()
