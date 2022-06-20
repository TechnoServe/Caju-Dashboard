from branca.element import Template, MacroElement

LayerControlToggler = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
        
        <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
        <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    
        <script>
    
            document.addEventListener("DOMContentLoaded", function(event) { 
                const layerControl = document.querySelector(".folium-map");
                leaflet_control_container = layerControl.childNodes[1];

                leaflet_top_right = leaflet_control_container.childNodes[1];

                leaflet_control_layers = leaflet_top_right.childNodes[1];
                
                clone = leaflet_top_right.childNodes[1].cloneNode(true);
                clone.setAttribute("id", "layerControlTogglerId");
                clone.className = "leaflet-control-layers leaflet-control-layers-collapsed leaflet-control"
                clone.removeChild(clone.lastChild);
                
                clone.addEventListener("click", function() {
                    const layerControl = document.querySelector(".folium-map");
                    leaflet_control_container = layerControl.childNodes[1];
                    leaflet_top_right = leaflet_control_container.childNodes[1];
                    layerController = leaflet_top_right.childNodes[2];
                    if(!event.detail || event.detail == 1){
                        if (layerController.getAttribute('hidden') !== null) {
                            layerController.removeAttribute("hidden", "");
                        } else {
                            layerController.setAttribute("hidden", "");
                        }
                    }
                });

                // Swap position
                const afterNode2 = clone.nextElementSibling;
                const parent = clone.parentNode;
                leaflet_control_layers.replaceWith(clone);
                leaflet_top_right.insertBefore(leaflet_control_layers, afterNode2);

                leaflet_control_layers.setAttribute("hidden", "");
            });
        </script>
        <style>
            #btn {
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 1000;
                background: white;
                border: none;
            }
        </style>
    </head>
    <body>
    </body>
</html>
{% endmacro %}"""

LayerControlLoader = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
        
        <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
        <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    
        <script>
    
            document.addEventListener("DOMContentLoaded", function(event) { 
                const layerControl = document.querySelector(".folium-map");
                leaflet_control_container = layerControl.childNodes[1];

                leaflet_top_right = leaflet_control_container.childNodes[1];

                leaflet_control_layers = leaflet_top_right.childNodes[1];
                
                leaflet_control_layers_list = leaflet_control_layers.childNodes[1];
                leaflet_control_layers_base = leaflet_control_layers_list.childNodes[0];
                leaflet_control_layers_overlays = leaflet_control_layers_list.childNodes[2];
                console.log(leaflet_control_layers_base)
                console.log(leaflet_control_layers_overlays)
            });
        </script>
        <style>
            #btn {
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 1000;
                background: white;
                border: none;
            }
        </style>
    </head>
    <body>
    </body>
</html>
{% endmacro %}"""

macro_toggler = MacroElement()
macro_toggler._template = Template(LayerControlToggler)

macro_loader = MacroElement()
macro_loader._template = Template(LayerControlLoader)
