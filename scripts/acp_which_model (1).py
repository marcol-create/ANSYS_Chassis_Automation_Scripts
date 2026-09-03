# Read-only probe: which model is active, and does it contain 'Seat'?
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()

def names(coll):
    try:
        return list(coll.keys())
    except Exception:
        try:
            return [getattr(x, "name", repr(x)) for x in coll]
        except Exception as e:
            return "cannot list: %s" % e

m = db.active_model
info = []
info.append("ACTIVE MODEL = %r" % getattr(m, "name", "?"))
try:
    info.append("all models in db = %r" % names(db.models))
except Exception as e:
    info.append("db.models err: %s" % e)
info.append("solid_models in active = %r" % names(m.solid_models))

# direct access tests (exact string, lowercase, trailing space)
for key in ["Seat", "seat", "Seat "]:
    try:
        v = m.solid_models[key]
        info.append("access [%r] -> OK" % key)
    except Exception as e:
        info.append("access [%r] -> FAIL (%s)" % (key, type(e).__name__))

# if another model has Seat, say so
try:
    for mname in names(db.models):
        try:
            mm = db.models[mname]
            if "Seat" in names(mm.solid_models):
                info.append("model %r HAS a 'Seat' solid model" % mname)
        except Exception:
            pass
except Exception:
    pass

raise RuntimeError("  ||  ".join(info))
