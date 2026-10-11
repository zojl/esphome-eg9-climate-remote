import esphome.codegen as cg

CODEOWNERS = ["@zojl"]
DEPENDENCIES = ["remote_transmitter"]
AUTO_LOAD = ["climate"]

eg9_climate_ns = cg.esphome_ns.namespace("eg9_climate")
