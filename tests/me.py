import eqpy
import json


def run():
    eqpy.OUT_put('params')
    cfg_file = eqpy.IN_get()
    params = [{'a': 1}, {'a': 2}]
    eqpy.OUT_put(json.dumps(params))
    r = eqpy.IN_get()
    print(r, flush=True)
    params = [{'a': 3}, {'a': 4}]
    eqpy.OUT_put(json.dumps(params))
    r = eqpy.IN_get()
    print(r, flush=True)
    eqpy.OUT_put("DONE")
    eqpy.OUT_put("BYE")
