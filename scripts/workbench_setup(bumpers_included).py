# =====================================================================
#  WORKBENCH: FULL SETUP (ACP + BUMPERS, NO ROLLCAGE)
# =====================================================================
#  Run from the Workbench Project window (start from an EMPTY project):
#     File > Scripting > Run Script File...  -> pick THIS file
#
#  Rebuilt from workbench_setup(bumpers_with_rollcage).py with the
#  rollcage removed:
#    1. Builds ACP Pre + 2 analysis + 2 bumper Mechanical Models
#    2. Imports material files (*Al_HC*, *CF_Limits*) into block A only
#    3. Prompts for a STEP file for chassis and each bumper
#    4. Runs Mechanical setup:
#         chassis  -> 1 mm thickness + Named Selection per body
#         bumpers  -> 1 mm thickness + 3 mm mesh + generate
#    5. Saves
# =====================================================================

import os

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
SEARCH_ROOTS = [os.path.expanduser("~")]
MATERIAL_NAME_KEYS = ["Al_HC", "CF_Limits"]
MATERIAL_EXTS = (".xml", ".engd", ".eng")
SKIP_DIRS = set(["appdata", "$recycle.bin", "windows", "program files",
                 "program files (x86)", "programdata", "node_modules", ".git",
                 "application data", "local settings", "my documents",
                 "cookies", "nethood", "printhood", "recent"])

# How to open Mechanical: "" (visible, most reliable) / "Interactive" / "Hidden"
EDIT_MODE = "Interactive"

# Fallback STEP paths if a file dialog is cancelled/unavailable ("" = skip)
FALLBACK_PATHS = {"Chassis panels": "", "Side bumper": "",
                  "Front bumper": ""}


# ---------------------------------------------------------------------
# Mechanical-side scripts (run INSIDE Mechanical via SendCommand)
# ---------------------------------------------------------------------
CHASSIS_CMD = '''
THICKNESS = Quantity("1 [mm]")
NAME_DELIMITER = "|"

def clean_name(raw):
    if NAME_DELIMITER and NAME_DELIMITER in raw:
        return raw.rsplit(NAME_DELIMITER, 1)[-1].strip()
    return raw.strip()

model  = ExtAPI.DataModel.Project.Model
bodies = model.GetChildren(DataModelObjectCategory.Body, True)
with Transaction():
    for body in bodies:
        try:
            body.Thickness = THICKNESS
        except Exception:
            pass
with Transaction():
    for body in bodies:
        face_ids = [face.Id for face in body.GetGeoBody().Faces]
        if not face_ids:
            continue
        sel = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
        sel.Ids = face_ids
        ns = model.AddNamedSelection()
        ns.Location = sel
        ns.Name = clean_name(body.Name)
'''

BUMPER_CMD = '''
THICKNESS    = Quantity("1 [mm]")
ELEMENT_SIZE = Quantity("3 [mm]")
model  = ExtAPI.DataModel.Project.Model
bodies = model.GetChildren(DataModelObjectCategory.Body, True)
with Transaction():
    for body in bodies:
        try:
            body.Thickness = THICKNESS
        except Exception:
            pass
mesh = model.Mesh
mesh.ElementSize = ELEMENT_SIZE
mesh.UseAdaptiveSizing = False
mesh.GenerateMesh()
'''

CMD_BY_KIND = {"chassis": CHASSIS_CMD, "bumper": BUMPER_CMD}


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------
def get_template(name, solver=None):
    try:
        if solver:
            return GetTemplate(TemplateName=name, Solver=solver)
        return GetTemplate(TemplateName=name)
    except Exception:
        if solver:
            return GetTemplate(TemplateName="%s (%s)" % (name, solver))
        raise


def find_material_files(roots, key):
    hits, seen, key_low = [], set(), key.lower()
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: None):
            dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
            for fname in filenames:
                low = fname.lower()
                if key_low in low and low.endswith(MATERIAL_EXTS):
                    full = os.path.join(dirpath, fname).replace("\\", "/")
                    if full not in seen:
                        seen.add(full); hits.append(full)
    try:
        hits.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    except Exception:
        pass
    return hits


def pick_step_file(label):
    try:
        import clr
        clr.AddReference("System.Windows.Forms")
        from System.Windows.Forms import OpenFileDialog, DialogResult
        from System.Threading import Thread, ThreadStart, ApartmentState
        holder = {"path": None}
        def _show():
            dlg = OpenFileDialog()
            dlg.Title = "Select STEP file for: %s" % label
            dlg.Filter = "STEP files (*.step;*.stp)|*.step;*.stp|All files (*.*)|*.*"
            dlg.RestoreDirectory = True
            if dlg.ShowDialog() == DialogResult.OK:
                holder["path"] = dlg.FileName
        t = Thread(ThreadStart(_show))
        t.SetApartmentState(ApartmentState.STA)
        t.Start(); t.Join()
        return holder["path"]
    except Exception as ex:
        print("  (file dialog unavailable: %s)" % ex)
        return None


def choose_geometry(label):
    path = pick_step_file(label)
    if not path:
        path = FALLBACK_PATHS.get(label, "")
    return path if path else None


def open_model(model):
    if EDIT_MODE == "Interactive":
        model.Edit(Interactive=False)
    elif EDIT_MODE == "Hidden":
        model.Edit(Hidden=True)
    else:
        model.Edit()


# =====================================================================
# 1. BUILD THE SCHEMATIC
# =====================================================================
sysA = get_template("ACP (Pre)").CreateSystem()
sysA.DisplayText = "Panels"
print("A created: Panels")

# materials into block A
eng = sysA.GetContainer(ComponentName="Engineering Data")
for key in MATERIAL_NAME_KEYS:
    files = find_material_files(SEARCH_ROOTS, key)
    if files:
        try:
            eng.Import(Source=files[0]); print("Imported '%s': %s" % (key, files[0]))
        except Exception as ex:
            print("Material import failed for '%s': %s" % (key, ex))
    else:
        print("WARNING: no material file matching '%s'" % key)

sysB = get_template("Static Structural", "ANSYS").CreateSystem(Position="Right", RelativeTo=sysA)
sysB.DisplayText = "Side Impact"
print("B created: Side Impact")

sysC = get_template("Structural Optimization", "ANSYS").CreateSystem(Position="Below", RelativeTo=sysB)
sysC.DisplayText = "Front Impact"
print("C created: Front Impact")

tmpl_mm = get_template("Mechanical Model")
sysD = tmpl_mm.CreateSystem(Position="Below", RelativeTo=sysA)
sysD.DisplayText = "Side bumper"
print("D created: Side bumper")

sysE = tmpl_mm.CreateSystem(Position="Below", RelativeTo=sysD)
sysE.DisplayText = "Front Bumper"
print("E created: Front Bumper")



# =====================================================================
# 2. GEOMETRY (via picker) + MECHANICAL SETUP
# =====================================================================
# (system, kind, picker label)
GEO_TASKS = [
    (sysA, "chassis",  "Chassis panels"),
    (sysD, "bumper",   "Side bumper"),
    (sysE, "bumper",   "Front bumper"),
]

for sysx, kind, label in GEO_TASKS:
    try:
        path = choose_geometry(label)
        if path:
            sysx.GetContainer(ComponentName="Geometry").SetFile(FilePath=path.replace("\\", "/"))
            print("Geometry set for '%s': %s" % (sysx.DisplayText, path))
        else:
            print("No file chosen for '%s' - skipping its setup." % sysx.DisplayText)
            continue
        comp = sysx.GetComponent(Name="Model"); comp.Refresh()
        model = sysx.GetContainer(ComponentName="Model")
        open_model(model)
        model.SendCommand(Language="Python", Command=CMD_BY_KIND[kind])
        model.Exit()
        print("Setup done (%s): %s" % (kind, sysx.DisplayText))
    except Exception as ex:
        print("ERROR on '%s': %s" % (label, ex))

try:
    Save(Overwrite=True); print("Project saved.")
except Exception as ex:
    print("Not saved yet (File > Save once): %s" % ex)

print("ALL DONE.")
