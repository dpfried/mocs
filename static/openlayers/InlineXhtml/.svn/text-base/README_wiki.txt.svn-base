= !InlineXhtml =
[[PageOutline]]

== Description ==
The !InlineXhtml Addin can be used for situations where server side
generation of, possibly interactive, layer tiles using (x)html is desired.
For example; server side generation of tiles using xhtml, html, canvas, svg, etc.
!InlineXhtml can be used for both native svg output from compatible WMS servers
and for adding scalable svg layers. 

== Compatibility ==

|| Addin Version || OpenLayers Version ||
|| [http://svn.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk trunk] || > r? ||

 * Added HTML5 support

 1.0 [http://svn.openlayers.org/sandbox/hhudson/addins/InlineXhtml/release/1.0 InlineXhtml v1.0]

Note: See ticket [http://trac.openlayers.org/ticket/2415 #2415] for history

== Examples ==

''Suitable for browsers supporting xhtml and svg;''[[BR]]

 * [http://dev.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/examples/example1.htm example1.htm] - An example using an svg layer and an xhtml layer.
 * [http://dev.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/examples/example2.htm example2.htm] - An example of a scalable layer.
 * [http://dev.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/examples/example3.htm example3.htm] - A non-interactive scalable layer.
 * [http://dev.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/examples/example4.htm example4.htm] - A non-interactive scalable OSM Mapnik export.
 * [http://dev.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/examples/example5.htm example5.htm] - A non-interactive WMS example.
 * Simple Interactivity test case 1; [http://dev.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/examples/example6.htm xhtml] and [http://dev.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/examples/example7.htm html5].

== Installation and Use ==

 1. Use subversion to check out the [http://svn.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/ InlineXhtml] addin.
 1. Place the [http://svn.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/lib/OpenLayers/Tile/InlineXhtml.js Tile/InlineXhtml.js] file in your [source:trunk/openlayers/lib/OpenLayers/Tile/ Tile] directory (or alternatively, place it elsewhere and add a {{{<script>}}} tag to your page that points to it).
 1. Place the [http://svn.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/lib/OpenLayers/Layer/WMS/InlineXhtml.js Layer/WMS/InlineXhtml.js] file in your [source:trunk/openlayers/lib/OpenLayers/Layer/WMS/ Layer/WMS] directory (or alternatively, place it elsewhere and add a {{{<script>}}} tag to your page that points to it).
 1. Place the [http://svn.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/lib/OpenLayers/Layer/InlineXhtml.js Layer/InlineXhtml.js] file in your [source:trunk/openlayers/lib/OpenLayers/Layer/ Layer] directory (or alternatively, place it elsewhere and add a {{{<script>}}} tag to your page that points to it).
 1. Place the [http://svn.openlayers.org/sandbox/hhudson/addins/InlineXhtml/trunk/lib/OpenLayers/Layer/ScalableInlineXhtml.js Layer/ScalableInlineXhtml.js] file in your [source:trunk/openlayers/lib/OpenLayers/Layer/ Layer] directory (or alternatively, place it elsewhere and add a {{{<script>}}} tag to your page that points to it).

 1. For example, add the following headers;
{{{
      <script src="../lib/OpenLayers/Tile/InlineXhtml.js"></script>
      <script src="../lib/OpenLayers/Layer/WMS/InlineXhtml.js"></script>
      <script src="../lib/OpenLayers/Layer/InlineXhtml.js"></script>
      <script src="../lib/OpenLayers/Layer/ScalableInlineXhtml.js"></script>
}}}
 1. Use the [wiki:Profiles build tools] to create a single file build (or link to your !OpenLayers.js file to run in development mode).
 1. Construct a map and add a WMS InlineXhtml layer with the following syntax:
{{{
var layer1 = new OpenLayers.Layer.WMS.InlineXhtml(
                  name,
                  url,
                  params,
                  options);
}}}
 1. Construct a map and add an InlineXhtml layer with the following syntax:
{{{
var layer1 = new OpenLayers.Layer.InlineXhtml(
                  name,
                  url,
                  params,
                  options);
}}}
 1. Construct a map and add a ScalableInlineXhtml layer with the following syntax:
{{{
var layer1 = new OpenLayers.Layer.ScalableInlineXhtml(
                  name,
                  url,
                  extent,
                  size,
                  options);
}}}
== Usage Notes ==

 1. By default the inline content will be parsed as xhtml.  Refer to the "isHtmlLayer" layer option for adding html layers.
 1. Because !InlineXhtml makes use of XMLHttpRequest and imports the inline content directly into the document (as tile contents), it would probably necessitate the use of a proxy server (eg, proxy.cgi) to retrieve layers from remote servers.

== Tile.InlineXhtml ==
This tile class issues an Ajax request to retrieve inline content
to be imported into the document tile.

== Layer.WMS.InlineXhtml ==
This subclass to Layer.WMS can be used to add a WMS layer to the
map where the output of the WMS server is (x)html (eg, svg).  For example;
{{{
var layer1 = new OpenLayers.Layer.WMS.InlineXhtml(
                  "Layer 1",
                  "http://<some_wms_service>",
                  {layers: 'abc', format: 'image/svg+xml'} );
}}}

== Layer.InlineXhtml ==
This layer class can be used to add a map layer where the
tile base url request parameters will be made up of; BBOX, 
PROJECTION, WIDTH, HEIGHT and the server response is expected
to be (x)html. 

=== Parameters ===
name - A name for the layer[[BR]]
url - Base url for the (x)html service[[BR]]
params - An object with key/value pairs that will be passed to the service[[BR]]
options - Hashtable of extra options to tag onto the layer[[BR]]

== Layer.ScalableInlineXhtml ==
This layer class is somewhat analogous to the Layer.Image class
but applies to inline (x)html.  In addition to the url for the 
scalable inline content (image), the layer extent also needs to be
specified.  If an optional size (physical pixel dimensions) parameter
is supplied then the maximum resolution for the layer will automatically
be determined.  In order for the layer to scale correctly when the map
zoom level is changed, the inline content should be natively scalable.

''Tip: If you are adding an svg image using Layer.ScalableInlineXhtml,
the outermost <svg> element should probably not have "width"
or "height" attributes specifying physical image dimensions (or 
the image may not be scalable).  If
so, consider removing those attributes.  Then, if there is no existing
"viewBox" attribute, consider including one that represents the initial image space.
If necessary, specifying how the viewBox fits to the 
image viewport can be done with the "preserveAspectRatio" attribute.
If the original "width" and "height" are in pixel dimensions, you can optionally
specify them in the Layer.ScalableInlineXhtml size parameter to set the maximum
resolution for the layer.

For example, instead of;
{{{
<svg width="1024" height="768" preserveAspectRatio="none" ...
}}}
Try;
{{{
<svg viewBox="0 0 1024 768" preserveAspectRatio="none" ...
}}}
''

=== Parameters ===
name - A name for the layer[[BR]]
url - Url for the (x)html content (image)[[BR]]
extent - The extent represented by the image (map dimensions)[[BR]]
size - The size (in pixels) of the image unscaled (optional)[[BR]]
options - Hashtable of extra options to tag onto the layer[[BR]]


== Layer.WMS.InlineXhtml, Layer.InlineXhtml and Layer.ScalableInlineXhtml Options ==

=== isHtmlLayer ===
This boolean parameter can be used to specify the type of the inline content.  By
default (isHtmlLayer is false) the inline content will be treated as xhtml and, as
such, it must be valid xml.  If this parameter is set to true the inline content
will be treated as a html fragment and simply passed directly to the browsers
html parser - which may be suitable for html5 layers for example.

=== fallbackToHtmlLayer ===
If this boolean parameter is set to true (and isHtmlLayer is false) then
the inline content will first be parsed as xhtml, should that parsing fail the
inline content will then be passed to the browsers html parser.  Note that due
to different browser implementations, some heuristics are used to determine if
the initial parsing is successful.  Defaults to false.

=== overflow ===
This style option is applied to layer tiles.  The default overflow 
setting is 'hidden'.  Assuming the server doesn't clip the tile 
contents to the viewport, setting overflow to 'visible' may provide 
contiguous effects/rendering for elements that cross tile boundaries.
Generally, html overflow is supported in most browsers, whereas svg 
overflow (outside main svg element) is supported to a lesser extent.

Example;
{{{
var layer1 = new OpenLayers.Layer.InlineXhtml(
                  "Layer 1",
                  "http://<some_(x)html_service>",
                  null,
                  {overflow: 'visible'} );
}}}

=== pointerEvents ===
This style option is applied to the layer.  For example, setting to 
'none', in supported browsers, will allow mouse events to be passed 
through to underlying layers meaning that a layer can be made 
transparent to mouse events.

Example;
{{{
var layer1 = new OpenLayers.Layer.InlineXhtml(
                  "Layer 1",
                  "http://<some_(x)html_service>",
                  null,
                  {pointerEvents: 'none'} );
}}}

The pointerEvents property can be set for other layer types as follows;
{{{
<layer1>.div.style.pointerEvents = 'none';
}}}

=== xhtmlContainerId ===
This string tag can be used to specify a container id for the inline xhtml.
The xhtml content will be retrieved and scanned for an element where the 
"id" attribute matches.  Then, only child nodes of such an element will be 
added to the tile.  This allows an entire xhtml document to be sent from
the server to the client but only those elements within the container 
added to the tile.  Applies only to xhtml layers.

Example;
{{{
var layer1 = new OpenLayers.Layer.InlineXhtml(
                  "Layer 1",
                  "http://<some_xhtml_service>",
                  null,
                  {xhtmlContainerId: 'abc'} );
}}}

Assuming the following is a server response for the tile, then
only the svg will be added to the tile;
{{{
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:svg="http://www.w3.org/2000/svg">
 <body>
  Tile contents ...
  <div id="abc">
   <svg width="256" height="256">
    ...
   </svg>
  </div>
 </body>
</html>
}}}

=== sendIdParams ===
This boolean parameter can be used to append a set of OpenLayers id 
parameters as part of the tile url request.  This may be useful for
server side operations where uniqueness needs to be maintained across 
the entire document not just across the tile.  For example; tile components 
such as element id's, style class names, inline scripting function names, 
etc, may need to be unique over the entire document not just over each tile.
The parameters that will be added to a tile request are;

|| Parameter Name || Parameter Value ||
|| OPENLAYERS_MAP_ID || <tile>.layer.map.id ||
|| OPENLAYERS_MAP_DIV_ID || <tile>.layer.map.div.id ||
|| OPENLAYERS_LAYER_ID || <tile>.layer.id ||
|| OPENLAYERS_TILE_ID || <tile>.id ||

Example;
{{{
var layer1 = new OpenLayers.Layer.InlineXhtml(
                  "Layer 1",
                  "http://<some_(x)html_service>",
                  null,
                  {sendIdParams: true} );
}}}

=== evaluatedParams ===
This hashtable is similar to the layer 'params' property, however parameters
specified here will be evaluated (client side) before being added to the tile
request.

Example;
{{{
var layer1 = new OpenLayers.Layer.InlineXhtml(
                  "Layer 1",
                  "http://<some_(x)html_service>",
                  null,
                  {evaluatedParams: {current_date: 'Date();', this_tile_id: 'this.id'}} );
}}}


== Tile.InlineXhtml Tuning Options ==

The tile tuning options would not normally need to be altered but they may change in subsequent releases of the InlineXhtml Addin.

=== xhtmlUseDocumentImportNodeForBrowsers ===
An array of browser names.  Entries in this array will cause the document.importNode method to be used when there
is a match on the browser name.  Otherwise the inline xhtml content will be traversed and added to the tile using
the Tile.InlineXhtml._importNode method.  This option will be ignored if an xhtmlContainerId property has been specified.
Applies only to xhtml layers.

=== xhtmlExecuteInlineScriptForBrowsers ===
An array of browser names.  Entries in this array will cause any inline script in the incoming xhtml content to be
manually executed after it is added to the tile when there is a match on the browser name.  Applies to xhtml layers.

=== htmlExecuteInlineScriptForBrowsers ===
An array of browser names.  Entries in this array will cause any inline script in the incoming html content to be
manually executed after it is added to the tile when there is a match on the browser name.  Applies to html layers.

=== useDocumentImportNodeForBrowsers ===
Deprecated - see xhtmlUseDocumentImportNodeForBrowsers.

=== executeInlineScriptForBrowsers ===
Deprecated - see xhtmlExecuteInlineScriptForBrowsers and htmlExecuteInlineScriptForBrowsers.
