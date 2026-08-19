import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import climate
from esphome.const import CONF_ID

CONF_TRANSMITTER = "transmitter"

eg9_climate_ns = cg.esphome_ns.namespace("eg9_climate")
EG9Climate = eg9_climate_ns.class_("EG9Climate", climate.Climate, cg.Component)

CONFIG_SCHEMA = climate.climate_schema(EG9Climate).extend(
    {
        cv.Required(CONF_TRANSMITTER): cv.use_id(cg.Component),
    }
).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await climate.register_climate(var, config)

    transmitter = await cg.get_variable(config[CONF_TRANSMITTER])
    cg.add(var.set_transmitter(transmitter))

