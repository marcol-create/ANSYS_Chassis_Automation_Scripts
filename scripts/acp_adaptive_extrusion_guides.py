# =====================================================================
#  ACP (Pre) -- ADAPTIVE flush-gap extrusion guides for the seat
# =====================================================================
#  Run INSIDE ACP (File > Run Script) AFTER acp_oss_plies_solids.py.
#
#  Every opening where a horizontal panel enters the angled seat should
#  have the seat wall made FLUSH (horizontal) to that panel. Since every
#  panel is horizontal, "flush" is always the same reorientation: rotate
#  the seat wall from its tilted normal to horizontal. That direction is
#  the seat's own normal with the vertical component removed -- derived
#  once from the seat rosette and applied to every gap.
#
#  ADAPTIVE: it does NOT use a fixed list of edge-set names. It discovers
#  every edge set in the model and guides each one. Make as many gap edge
#  sets as you like, name them whatever -- all get flushed. (If you also
#  make edge sets that are NOT seat gaps, set NAME_FILTER to a substring
#  they share, or list them explicitly in EDGE_SETS.)
# =====================================================================

# ---------------- CONFIG ----------------
SEAT_SET       = "Seat"     # seat solid model name (trailing space tolerated)
SEAT_ROSETTE   = "Seat"     # rosette whose Z is normal to the seat face

# Which edge sets to guide:
EDGE_SETS      = []         # [] = AUTO-DISCOVER every edge set in the model.
                            # Or list exact names to restrict to those.
NAME_FILTER    = ""         # if auto-discovering, only edge sets whose name
                            # contains this substring (case-insensitive). "" = all.

UP_AXIS        = (0.0, 0.0, 1.0)   # vertical axis; use (0,1,0) if Y is up
GUIDE_FLIP     = False             # flip the horizontal direction if walls tilt the WRONG way
PER_GAP_FLIP   = {}                # e.g. {"EdgeSet3": True} to flip just one opening
FORCE_DIRECTION = None             # (x,y,z) to override the derived horizontal entirely

GUIDE_RADIUS   = 35.0              # morph region (model units). ~3-5x local element size.
GUIDE_DEPTH    = 1.0
PER_GAP_RADIUS = {}                # e.g. {"EdgeSet3": 20.0} for one gap

DO_UPDATE        = True
REPLACE_EXISTING = True            # delete + recreate guides so re-runs are clean

# ---------------- MODEL ----------------
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model

import math

def _unit(v):
    if v is None:
        return None
    m = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return None if m < 1e-9 else (v[0] / m, v[1] / m, v[2] / m)

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def get_item(collection, name):
    try:
        return collection[name]
    except Exception:
        pass
    try:                                   # whitespace/case tolerant (matches "Seat " etc.)
        target = name.strip().lower()
        for k in collection.keys():
            if k.strip().lower() == target:
                return collection[k]
    except Exception:
        pass
    return None

def rosette_normal(ros):
    if ros is None:
        return None
    for a in ["normal", "dir3", "dir_3", "direction_3", "z_direction", "n"]:
        try:
            u = _unit(tuple(getattr(ros, a)))
            if u:
                return u
        except Exception:
            pass
    for a1, a2 in [("dir1","dir2"), ("dir_1","dir_2"),
                   ("direction_1","direction_2"), ("x_direction","y_direction")]:
        try:
            u = _unit(_cross(tuple(getattr(ros, a1)), tuple(getattr(ros, a2))))
            if u:
                return u
        except Exception:
            pass
    return None

def flatten_to_horizontal(v, up):
    up = _unit(up)
    if up is None or v is None:
        return None
    d = v[0]*up[0] + v[1]*up[1] + v[2]*up[2]
    return _unit((v[0]-d*up[0], v[1]-d*up[1], v[2]-d*up[2]))

def guide_exists(sm, gname):
    try:
        return sm.extrusion_guides[gname] is not None
    except Exception:
        return False

def delete_guide(sm, gname):
    try:
        g = sm.extrusion_guides[gname]
    except Exception:
        return False
    for attempt in (lambda: g.delete(),
                    lambda: sm.remove_extrusion_guide(g),
                    lambda: sm.remove_extrusion_guide(gname)):
        try:
            attempt(); return True
        except Exception:
            pass
    try:
        del sm.extrusion_guides[gname]; return True
    except Exception:
        return False

# ---------------- seat solid model ----------------
seat_sm = get_item(model.solid_models, SEAT_SET)
if seat_sm is None:
    raise RuntimeError("Seat solid model '%s' not found. Available: [%s]"
                       % (SEAT_SET, ", ".join(model.solid_models.keys())))

# ---------------- the single horizontal direction (from the seat angle) ----------------
if FORCE_DIRECTION is not None:
    base_dir, dsrc = _unit(tuple(FORCE_DIRECTION)), "forced"
else:
    n_seat = rosette_normal(get_item(model.rosettes, SEAT_ROSETTE))
    base_dir = flatten_to_horizontal(n_seat, UP_AXIS)
    dsrc = "flattened seat normal"
if base_dir is None:
    raise RuntimeError("Could not derive the horizontal direction. Seat rosette '%s' "
                       "normal missing or vertical. Set FORCE_DIRECTION, or check the "
                       "seat rosette's Z is normal to the seat face." % SEAT_ROSETTE)

# ---------------- discover the edge sets ----------------
if EDGE_SETS:
    targets = [n for n in EDGE_SETS]
else:
    targets = list(model.edge_sets.keys())
    if NAME_FILTER:
        nf = NAME_FILTER.strip().lower()
        targets = [n for n in targets if nf in n.lower()]

if not targets:
    raise RuntimeError("No edge sets to guide. edge_sets in model: [%s]  (NAME_FILTER=%r)"
                       % (", ".join(model.edge_sets.keys()), NAME_FILTER))

# ---------------- one guide per discovered edge set ----------------
made, notes = 0, []
for esname in targets:
    es = get_item(model.edge_sets, esname)
    if es is None:
        notes.append("%s: edge set not found" % esname)
        continue

    d = base_dir
    if GUIDE_FLIP or PER_GAP_FLIP.get(esname, False):
        d = (-d[0], -d[1], -d[2])
    radius = PER_GAP_RADIUS.get(esname, GUIDE_RADIUS)
    gname = "%s_flush" % esname

    if guide_exists(seat_sm, gname):
        if REPLACE_EXISTING:
            if not delete_guide(seat_sm, gname):
                notes.append("%s: exists, could not delete (remove it in the tree)" % gname)
                continue
        else:
            notes.append("%s: already exists (REPLACE_EXISTING off)" % gname)
            continue

    try:
        seat_sm.create_extrusion_guide(name=gname, edge_set=es,
                                       direction=d, radius=radius, depth=GUIDE_DEPTH)
        made += 1
        notes.append("%s: OK (r=%.0f)" % (gname, radius))
    except Exception as ex:
        raise RuntimeError("create_extrusion_guide failed for '%s': %s" % (esname, ex))

# ---------------- update ----------------
updated = False
if DO_UPDATE and made:
    try:
        model.update(); updated = True
    except Exception as ex:
        notes.append("model.update() raised: %s" % ex)

# ---------------- always-visible summary ----------------
head = ("DONE (not an error): guided %d of %d edge sets, updated=%s. "
        "dir=(%.3f,%.3f,%.3f) [%s]. Check upside-down/removed element messages; "
        "flip via GUIDE_FLIP (all) or PER_GAP_FLIP (one) if a wall tilts the wrong way."
        % (made, len(targets), updated, base_dir[0], base_dir[1], base_dir[2], dsrc)) \
       if made else \
       ("NOTHING GUIDED. targets=[%s] edge_sets=[%s]"
        % (", ".join(targets), ", ".join(model.edge_sets.keys())))
raise RuntimeError(head + "  ||  " + "  ||  ".join(notes))
