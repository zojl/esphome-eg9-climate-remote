import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import climate, remote_transmitter, select
from esphome.const import CONF_ID, CONF_NAME

from . import eg9_climate_ns

AUTO_LOAD = ["select"]

CONF_TRANSMITTER = "transmitter"
CONF_VANE_POSITION = "vane_position"
CONF_VANE_SELECT_NAME = "vane_select_name"

EG9Climate = eg9_climate_ns.class_("EG9Climate", climate.Climate, cg.Component)
EG9VaneSelect = eg9_climate_ns.class_("EG9VaneSelect", select.Select)

VANE_SELECT_SCHEMA = select.select_schema(EG9VaneSelect)


def validate_vane_position(value):
    if isinstance(value, str):
        value = {CONF_NAME: value}
    return VANE_SELECT_SCHEMA(value)


def validate_vane_select_name(value):
    return VANE_SELECT_SCHEMA({CONF_NAME: cv.string(value)})


CONFIG_SCHEMA = climate.climate_schema(EG9Climate).extend(
    {
        cv.Required(CONF_TRANSMITTER): cv.use_id(remote_transmitter.RemoteTransmitterComponent),
        cv.Optional(CONF_VANE_POSITION): validate_vane_position,
        cv.Optional(CONF_VANE_SELECT_NAME): validate_vane_select_name,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await climate.register_climate(var, config)

    transmitter = await cg.get_variable(config[CONF_TRANSMITTER])
    cg.add(var.set_transmitter(transmitter))

    vane_conf = None
    if CONF_VANE_POSITION in config:
        vane_conf = config[CONF_VANE_POSITION]
    elif CONF_VANE_SELECT_NAME in config:
        vane_conf = config[CONF_VANE_SELECT_NAME]

    if vane_conf is not None:
        vane_var = await select.new_select(
            vane_conf,
            options=[
                "Auto",
                "Top",
                "Medium-Top",
                "Medium",
                "Medium-Bottom",
                "Bottom",
            ],
        )
        cg.add(vane_var.set_parent(var))
        cg.add(var.set_vane_select(vane_var))


