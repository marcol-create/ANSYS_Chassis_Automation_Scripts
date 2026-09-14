# ANSYS Chassis Automation Scripts

Scripts for setting up the Sunstruck chassis in ANSYS Workbench and ACP. They handle geometry imports, named selections, composite layup objects, and parts of the meshing setup. Chassis meshing, rosette orientation, and draping still need attention by hand.

## Before starting

Prepare the CAD in Fusion: offset the chassis surfaces by 0.00 mm and export them as STEP geometry. Export the front bumper, side bumper, and rollcage separately if using the full setup.

Download the scripts from [scripts/](scripts/) and the material files from [materials/](materials/). The Workbench scripts search your user folder for material filenames containing `Al_HC` and `CF_Limits`; adjust `SEARCH_ROOTS` at the top of the script if you keep them elsewhere.

Run the Workbench scripts inside Workbench and the ACP scripts inside ACP.

## Workbench setup

Start with an empty Workbench project. Open **File → Scripting → Run Script File** and choose a setup script:

- [workbench_setup(just_acp).py](scripts/workbench_setup%28just_acp%29.py) creates the ACP (Pre) system, imports the material data and chassis geometry, assigns 1 mm surface thickness, and creates a named selection for each body.
- [workbench_setup(bumpers_with_rollcage).py](scripts/workbench_setup%28bumpers_with_rollcage%29.py) adds side and front bumper Mechanical models, a rollcage model, a Static Structural system named Side Impact, and a Structural Optimization system named Front Impact. Geometry prompts appear in this order: chassis, side bumper, front bumper, rollcage.

The full setup uses a 3 mm bumper mesh and 1 mm bumper surface thickness. The rollcage uses `ROLLCAGE_SIZE = 2 mm` and attempts a MultiZone mesh. Adjust that size for the tube wall thickness. The current script does not merge the rollcage bodies.

The file `workbench_setup(bumpers_included).py` currently contains Markdown documentation rather than executable Python, so it cannot be used as a setup script in its present form.

Save the Workbench project manually if the script's save attempt fails.

<img width="2560" height="1528" alt="ACP Workbench setup" src="https://github.com/user-attachments/assets/ecf6b3ed-9fdf-450a-bd1f-79e01b3e82bb" />

<img width="2560" height="1528" alt="Bumper setup in Workbench" src="https://github.com/user-attachments/assets/e8c1fed6-32fb-4de7-b3f2-82b00256fe39" />

<img width="2560" height="1600" alt="Structural analysis setup" src="https://github.com/user-attachments/assets/b690991e-21c5-437b-bdd1-010254c5b993" />

## Chassis mesh and named selections

Open the ACP Mechanical model and generate the chassis mesh. Choose the element size and local refinements for the analysis you plan to run.

<img width="2560" height="1540" alt="Chassis mesh in Mechanical" src="https://github.com/user-attachments/assets/cd505e9f-45f0-4a9a-a5b1-fe7f8f1bc9b8" />

If using the seat-gap extrusion guides, create four named selections now: `EdgeSet1`, `EdgeSet2`, `EdgeSet3`, and `EdgeSet4`. Each should contain the three edges of one seat gap. Keep the seat body named `Seat`.

Update the ACP (Pre) setup so the mesh and named selections reach ACP. The gap selections must appear as edge sets before running the guide script.

## ACP layup

Run these scripts from **File → Run Script** in ACP, starting with a clean model.

1. Run [acp_materials_rosettes.py](scripts/acp_materials_rosettes.py). It uses the imported material data to create CF and HC fabrics, the `Full Panel` stackup, and a centered rosette for each panel element set. It skips `All_Elements`.
2. Orient each rosette manually. Check its direction, flip, and offset direction before continuing.
3. Run [acp_oss_plies_solids.py](scripts/acp_oss_plies_solids.py). It creates an Oriented Selection Set (OSS), Modeling Group, Full Panel ply, and Solid Model for each panel set, with Analysis Ply Wise extrusion.
4. Review the draping setup and adjust it where needed.

The Full Panel stackup is:

```text
Carbon fiber       0°
Carbon fiber      90°
Aluminum honeycomb 0°
Carbon fiber       0°
Carbon fiber      90°
```

The fabric thickness settings are `CF_THICKNESS = 0.127` and `HC_THICKNESS = 12.192`. Check these against the model's unit system and intended panel construction.

Objects are linked by matching names. Avoid renaming element sets between scripts.

<img height="460" alt="ACP fabrics, stackup, and rosettes" src="https://github.com/user-attachments/assets/13564262-c9be-40b3-acc7-a719828bf01a" />

<img height="460" alt="ACP oriented selection sets and modeling groups" src="https://github.com/user-attachments/assets/fccf9a34-4582-4a3e-9a8b-fa1b4c5328a8" />

<img height="460" alt="ACP solid models" src="https://github.com/user-attachments/assets/4b692e55-4761-425c-a9fe-2e7063166209" />

## Seat-gap extrusion guides (optional)

The tilted seat extrudes normal to its face. At the gaps where horizontal supports pass through, this can leave a wedge-shaped space between the gap wall and the support.

Run [acp_script_gap_extrusion_guides.py](scripts/acp_script_gap_extrusion_guides.py) after the solid-model script. It adds local extrusion guides to the existing `Seat` solid model using `EdgeSet1` through `EdgeSet4`.

The settings at the top of the script are specific to this chassis:

- `FIXED_HORIZONTAL` contains a direction for each gap. These entries take precedence over `DIRECTION_MODE`, including its default `"support"` setting.
- `GAP_SUPPORT` maps the four edge sets to `LTopVertSupp`, `LBottomVertSupp`, `RTopVertSupp`, and `RBottomVertSupp`. Support-based directions are used only for gaps without a fixed override.
- `UP_AXIS` is Z-up. The `"seat_normal"` direction mode uses the `Seat` rosette's normal with its vertical component removed.
- `GUIDE_FLIP` reverses all guide directions; `PER_GAP_FLIP` reverses individual gaps.
- `GUIDE_RADIUS` defaults to `35.0`, with individual adjustments available through `PER_GAP_RADIUS`. `GUIDE_DEPTH` defaults to `1.0`.

Check a section through each gap after running. If a wedge gets wider, reverse that gap's direction. If the wall distorts, reduce its guide radius and inspect again.

By default, `REPLACE_EXISTING = True` deletes and recreates existing guides, so rerunning applies changed settings. With `DO_UPDATE = True`, the script also attempts an ACP update when it creates guides.

The script deliberately raises a `RuntimeError` at the end to display its summary. Read the created count, update status, and per-gap messages to tell whether it succeeded.

The guides adjust the gap geometry. Contact between the seat and supports still needs to be defined in Mechanical for load transfer.

Update ACP, inspect the resulting solids, and return to Workbench to continue the structural analyses.
