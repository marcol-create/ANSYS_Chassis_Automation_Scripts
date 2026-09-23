# ANSYS Chassis (Semi) Automation Scripts

Python scripts that automate the repetitive parts of setting up composite and bumper analyses for the Sunstruck chassis in ANSYS Workbench and ACP.

## Included Scripts

`workbench_setup(just_acp).py` creates an ACP-only Workbench project. Prompts for the chassis geometry, imports the material data from your computer, and completes the initial Mechanical setup (thickness plus named selections).

`workbench_setup(bumpers_included).py` creates the full Workbench project with ACP, Front Bumper, and Side Bumper systems. Imports all geometry, meshes the bumper models, and creates the Static Structural and Structural Optimization analyses.

`workbench_setup(with_rollcage).py` is the same as the bumper workflow, with an additional Rollcage Mechanical Model that imports the rollcage geometry, merges its bodies into one, and generates a plain 10 mm mesh using the default Structural Steel material.

`acp_materials_rosettes.py` creates the Carbon Fiber and Honeycomb materials, the Full Panel layup, and one centered rosette for every element set (orientation is still manual).

`acp_oss_plies_solids.py` creates the Oriented Selection Sets (OSSs), Modeling Groups, plies, and solid models from the finalized rosettes.

`acp_gap_extrusion_guides.py` adds a localized extrusion guide to each seat gap so the gap walls extrude flush (horizontal) to the support panels passing through them, while the seat body keeps extruding normal to its own face. Run last.

## Quick Workflow

Before opening ANSYS, prepare the CAD in Fusion by offsetting all chassis surfaces by 0.00 mm, saving the bumper parts as separate STEP files, and exporting everything as `.step`.

If needed, download the material data files included in this repository.

1. Run a Workbench setup script.
   - Open Workbench, then File → Scripting → Run Script File.
   - Run one of `workbench_setup(just_acp).py`, `workbench_setup(bumpers_included).py`, or `workbench_setup(with_rollcage).py`.
   - The script imports the geometry, loads the material data, creates the named selections, and sets up the Mechanical models. The bumper and rollcage versions also generate their meshes and create the structural analyses.

2. Generate the chassis mesh.
   - Open the ACP Mechanical model and generate the chassis mesh using the sizing appropriate for your analysis.

3. Create the gap edge sets (only if using the flush-gap guides).
   - Still in the ACP Mechanical model, create one Named Selection per seat gap, each scoping the three edges of that gap, named `EdgeSet1`, `EdgeSet2`, `EdgeSet3`, `EdgeSet4`.
   - Confirm the seat's surface body / element set is named `Seat` (the guide script targets that name).
   - Update the ACP (Pre) setup so the named selections propagate into ACP as edge sets.

4. Create the ACP model.
   - In ACP, File → Run Script, run `acp_materials_rosettes.py`.
   - The script creates the Carbon Fiber and Honeycomb materials, the Full Panel layup, and one centered rosette for every element set.

5. Orient the rosettes.
   - Manually set the direction, flip, and offset direction for each rosette.

6. Generate the remaining ACP objects.
   - Run `acp_oss_plies_solids.py`.
   - The script creates the OSSs, Modeling Groups, plies, and solid models, linking everything by matching names.
   - Assign draping where needed.

7. Make the seat gaps flush (optional, run last).
   - Run `acp_gap_extrusion_guides.py` after `acp_oss_plies_solids.py`, once the `Seat` solid model exists.
   - It adds one extrusion guide per gap (`EdgeSet1` through `EdgeSet4`) on the `Seat` solid model, so those gaps extrude flush to the support panels. Only the seat is affected; every other panel is untouched. See section 7 for the check-and-flip step.

8. Update ACP.
   - Update the ACP model, then return to Workbench to continue with the structural analyses.

## Manual Steps

These steps are still done by hand:

- Mesh the chassis
- Create the gap edge-set named selections (`EdgeSet1` through `EdgeSet4`), three edges each
- Orient the rosettes
- Assign draping
- Check and (if needed) flip the gap guide direction after running `acp_gap_extrusion_guides.py`

## 1. Workbench Setup

### Option A: ACP Only

Required geometry: chassis panels STEP file.

In ANSYS Workbench:

```text
File → Scripting → Run Script File
```

Run:

```text
workbench_setup(just_acp).py
```

Select the chassis STEP file when prompted.

The script:

- Creates an ACP (Pre) system
- Imports the Carbon Fiber and Aluminum Honeycomb material data
- Imports the chassis geometry
- Opens ACP Mechanical
- Assigns a 1 mm thickness to every surface body
- Creates a Named Selection for every body
- Saves the Workbench project

<img width="2560" height="1528" alt="image" src="https://github.com/user-attachments/assets/ecf6b3ed-9fdf-450a-bd1f-79e01b3e82bb" />

### Option B: ACP + Bumpers

Required geometry: chassis panels, front bumper, and side bumper STEP files.

Run:

```text
workbench_setup(bumpers_included).py
```

Select the chassis, front bumper, and side bumper STEP files when prompted.

The script creates:

ACP

- ACP (Pre) system
- Imports Carbon Fiber and Aluminum Honeycomb material data
- Imports the chassis geometry
- Opens ACP Mechanical
- Assigns a 1 mm thickness to every surface body
- Creates a Named Selection for every body

<img width="2560" height="1528" alt="image" src="https://github.com/user-attachments/assets/ecf6b3ed-9fdf-450a-bd1f-79e01b3e82bb" />

Bumpers

- Front and Side Bumper Mechanical systems
- Imports the bumper geometry
- Assigns a 1 mm thickness to all surface bodies
- Generates a 3 mm mesh
- Creates Static Structural analyses
- Creates Structural Optimization analyses
- Saves the Workbench project

<img width="2560" height="1528" alt="image" src="https://github.com/user-attachments/assets/e8c1fed6-32fb-4de7-b3f2-82b00256fe39" />

<img width="2560" height="1600" alt="image" src="https://github.com/user-attachments/assets/b690991e-21c5-437b-bdd1-010254c5b993" />

### Option C: ACP + Bumpers + Rollcage

Same as Option B, with an additional Rollcage Mechanical Model.

Required geometry: chassis panels, front bumper, side bumper, and rollcage (solid hollow tubes) STEP files.

Run:

```text
workbench_setup(with_rollcage).py
```

Select the geometry files in this order:

1. Chassis
2. Front bumper
3. Side bumper
4. Rollcage

Everything from Option B, plus:

Rollcage

- Imports the rollcage geometry
- Uses the default Structural Steel material
- Merges all rollcage bodies into a single body (if not already one)
- Generates a plain 10 mm mesh

## 2. Mesh the Chassis

Open the ACP Mechanical model and generate the chassis mesh.

Choose the element size and any local refinement appropriate for your analysis.

<img width="2560" height="1540" alt="image" src="https://github.com/user-attachments/assets/cd505e9f-45f0-4a9a-a5b1-fe7f8f1bc9b8" />

## 3. Create the Gap Edge Sets (optional, for flush gaps)

If you want the seat gaps to sit flush against the support panels that pass through them, create the edge sets now, while you are still in the ACP Mechanical model.

For each seat gap:

- Create a Named Selection scoped to the three edges of that gap.
- Name them `EdgeSet1`, `EdgeSet2`, `EdgeSet3`, `EdgeSet4` (one per gap).

Also confirm the seat's surface body / element set is named `Seat`, since `acp_gap_extrusion_guides.py` looks the seat solid model up by that exact name.

Then update the ACP (Pre) setup so these named selections propagate into ACP as edge sets. They do not appear in `model.edge_sets` until the setup is updated.

Skip this section if you are not using the flush-gap guides.

## 4. Materials, Layup & Rosettes

In ACP:

```text
File → Run Script
```

Run:

```text
acp_materials_rosettes.py
```

The script creates:

- Carbon Fiber material
- Honeycomb material
- Full Panel layup

```text
Carbon Fiber (0°)
Carbon Fiber (90°)
Aluminum Honeycomb (0°)
Carbon Fiber (0°)
Carbon Fiber (90°)
```

- One centered rosette for every element set

<img height="460" alt="image" src="https://github.com/user-attachments/assets/13564262-c9be-40b3-acc7-a719828bf01a" />

## 5. Orient the Rosettes

Before continuing, orient each rosette manually.

Check the:

- Direction
- Flip
- Offset direction

Each panel may require a different orientation.

The seat rosette (named `Seat`) should have its blue Z axis normal to the seat face. The flush-gap script reads this normal to derive the horizontal guide direction, so getting it right here also drives step 7.

## 6. OSSs, Plies & Solid Models

In ACP:

```text
File → Run Script
```

Run:

```text
acp_oss_plies_solids.py
```

The script creates:

- One Oriented Selection Set (OSS) per element set
- One Modeling Group per element set
- One Full Panel ply per Modeling Group
- One Solid Model per element set
- Analysis Ply Wise extrusion
- Links all ACP objects by matching names

<img height="460" alt="image" src="https://github.com/user-attachments/assets/fccf9a34-4582-4a3e-9a8b-fa1b4c5328a8" />

<img height="460" alt="image" src="https://github.com/user-attachments/assets/4b692e55-4761-425c-a9fe-2e7063166209" />

## 7. Flush Gap Extrusion Guides (optional)

Run this last. `acp_gap_extrusion_guides.py` is the final ACP script, run after `acp_oss_plies_solids.py` and before the final ACP update / return to Workbench. It attaches guides as children of the existing `Seat` solid model, so that solid model must already have been created by `acp_oss_plies_solids.py`. Running it earlier will fail because there is no solid model to attach to. It does not replace or rebuild any solid model; it adds four guides to the seat and re-extrudes only that one part on the next update. Every other panel is left exactly as `acp_oss_plies_solids.py` produced it.

It is also idempotent and standalone: it only touches `Seat` and the four gap edge sets, reads nothing it doesn't need, and skips guides that already exist, so it is safe to re-run on its own (for example after flipping a direction) without re-running the earlier scripts.

The seat wall sits at an angle (around 65°) and extrudes normal to its own face, which is correct, but the horizontal support panels pass through the seat gaps. Because the gap walls also extrude along the tilted seat normal, they only meet the horizontal supports along a single line, leaving a wedge-shaped void.

`acp_gap_extrusion_guides.py` fixes this by adding one extrusion guide per gap, scoped to that gap's edge set. Each guide re-points only those edges along a horizontal direction, so the four gap walls lie flat (horizontal) and sit flush against the supports. The rest of the seat, and every other panel, is untouched and keeps extruding normally.

### Prerequisites

- `acp_oss_plies_solids.py` has been run (the `Seat` solid model must already exist).
- Edge sets `EdgeSet1` through `EdgeSet4` exist (see section 3), three edges each.
- The seat solid model / element set / rosette are all named `Seat`.

### Run

In ACP, File → Run Script, run:

```text
acp_gap_extrusion_guides.py
```

### Key config (top of the script)

- `SEAT_SET` / `SEAT_ROSETTE`: names of the seat solid model and its rosette (default `"Seat"`).
- `EDGE_SETS`: the gap edge sets to guide (default `EdgeSet1` through `EdgeSet4`).
- `UP_AXIS`: vertical axis; `(0,0,1)` for Z-up.
- `GUIDE_FLIP`: negate the horizontal direction if the wedge gets worse.
- `GUIDE_RADIUS`: sphere of influence. Keep tight so the tilt stays local.
- `FIXED_HORIZONTAL`: override the derived direction; also accepts a per-gap dict.

The horizontal direction is derived automatically by taking the seat rosette's normal and flattening out the vertical component, so there's no need to compute it by hand.

### Check after running

Take a section cut through each gap and look at the wall:

- Wedge closed, wall flat on the support: done.
- Wedge got wider: the direction is reversed. Set `GUIDE_FLIP = True` and re-run.
- Wall looks warped or distorted: lower `GUIDE_RADIUS`, or split the gap's third edge (the one running along the guide direction) onto its own guide.

### Notes

- Ply orientation is preserved. The guide only re-points mesh nodes; fiber directions and ply angles at the gaps come from the same `Seat` rosette/OSS as the rest of the seat. There is no separate composite orientation at the gaps.
- The guide gives geometric flushness only. The seat and support meshes are not node-conformal at the interface, so still define a bonded (or frictional) contact between them in Mechanical for load transfer.
- Re-running is safe: guides already present are skipped. Delete a guide in the tree (or set `SKIP_IF_EXISTS = False`) to recreate it with different settings.

### Final ACP Model

Update the ACP model, then return to Workbench to continue with the structural analyses.

<img width="1484" height="896" alt="image" src="https://github.com/user-attachments/assets/9f73a316-3284-4284-a62c-d52c181f779e" />


## Notes

- Run each ACP script once on a clean ACP model.
- Generate the chassis mesh before running the ACP scripts.
- Create the `EdgeSet1` through `EdgeSet4` named selections (three edges each) before running `acp_gap_extrusion_guides.py`, and update the ACP (Pre) setup so they propagate.
- The seat body must be named `Seat` for the flush-gap script to find it.
- The bumper meshes are generated automatically by `workbench_setup(bumpers_included).py`.
- The rollcage is merged into one body and meshed at 10 mm automatically by `workbench_setup(with_rollcage).py`.
- All ACP objects are linked by matching names, so avoid renaming element sets after the initial setup.
