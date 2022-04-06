
from collections import OrderedDict
from branca.element import MacroElement
from folium.map import Layer

from folium.utilities import parse_options

from jinja2 import Template


class CustomLayerControl(MacroElement):
    """
    Creates a LayerControl object to be added on a folium map.

    This object should be added to a Map object. Only Layer children
    of Map are included in the layer control.

    Parameters
    ----------
    position : str
          The position of the control (one of the map corners), can be
          'topleft', 'topright', 'bottomleft' or 'bottomright'
          default: 'topright'
    collapsed : bool, default True
          If true the control will be collapsed into an icon and expanded on
          mouse hover or touch.
    autoZIndex : bool, default True
          If true the control assigns zIndexes in increasing order to all of
          its layers so that the order is preserved when switching them on/off.
    **kwargs
        Additional (possibly inherited) options. See
        https://leafletjs.com/reference-1.6.0.html#control-layers

    """
    _template = Template("""
        {% macro script(this,kwargs) %}
            var {{ this.get_name() }} = {
                base_layers : {
                    {%- for key, val in this.base_layers.items() %}
                    {{ key|tojson }} : {{val}},
                    {%- endfor %}
                },
                overlays :  {
                    {%- for key, val in this.overlays.items() %}
                    {{ key|tojson }} : {{val}},
                    {%- endfor %}
                },
            };
            L.control.layers(
                {{ this.get_name() }}.base_layers,
                {{ this.get_name() }}.overlays,
                {{ this.options|tojson }}
            ).addTo({{this._parent.get_name()}});
            {%- for val in this.layers_untoggle.values() %}
            {{ val }}.remove();
            {%- endfor %}
        {% endmacro %}
        """)

    def __init__(self, position='topright', collapsed=True, autoZIndex=True,
                 **kwargs):
        super(CustomLayerControl, self).__init__()
        self._name = 'LayerControl'
        self.options = parse_options(
            position=position,
            collapsed=collapsed,
            autoZIndex=autoZIndex,
            **kwargs
        )
        self.base_layers = OrderedDict()
        self.overlays = OrderedDict()
        self.layers_untoggle = OrderedDict()

    def reset(self):
        self.base_layers = OrderedDict()
        self.overlays = OrderedDict()
        self.layers_untoggle = OrderedDict()

    def render(self, **kwargs):
        """Renders the HTML representation of the element."""
        for item in self._parent._children.values():
            if not isinstance(item, Layer) or not item.control:
                continue
            key = item.layer_name
            if not item.overlay:
                self.base_layers[key] = item.get_name()
                if len(self.base_layers) > 1:
                    self.layers_untoggle[key] = item.get_name()
            else:
                self.overlays[key] = item.get_name()
                if not item.show:
                    self.layers_untoggle[key] = item.get_name()
        super(CustomLayerControl, self).render()
