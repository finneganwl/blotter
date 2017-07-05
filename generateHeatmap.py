import csv, config

topics = {'total': 4, 'substances': 5, 'noise': 6}
TOPIC = 'total' # USE THIS TO SELECT TOPIC TO DISPLAY

#locationsFile = 'outputs/locations.csv'
locationsFile = 'outputs/dormsCount.csv'

heatMapData = ''
with open(locationsFile, 'r') as csvfile:
	next(csvfile) # skip header line
	reader = csv.reader(csvfile)
	for row in reader:
		lat = row[2]
		lng = row[3]
		weight = row[topics[TOPIC]]
		if lat != '0' and weight != '0':
			heatMapData += '{location: new google.maps.LatLng(' + lat + ', ' + lng + '), weight: ' + weight + '},\n'

apiKey = config.MAPS_API_KEY

top = """
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>Heatmap</title>
    <style>
      /* Always set the map height explicitly to define the size of the div
       * element that contains the map. */
      #map {
        height: 100%;
      }
      /* Optional: Makes the sample page fill the window. */
      html, body {
        height: 100%;
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <div id="map"></div>
    <script>
      function initMap() {
        // Create the map.
        var map = new google.maps.Map(document.getElementById("map"), {
          zoom: 15,
          center: {lat: 42.056204, lng: -87.677112},
          mapTypeId: 'terrain'
        });

        var heatMapData = [
"""

bottom = """
        ]

        var heatmap = new google.maps.visualization.HeatmapLayer({
          data: heatMapData,
          radius: 60
        });
        heatmap.setMap(map);
      }
    </script>
    <script type="text/javascript"
      src="https://maps.googleapis.com/maps/api/js?key=
""" + apiKey + """
&libraries=visualization&callback=initMap">
    </script>
  </body>
</html>
"""

heatmapFile = 'heatmap.html'
with open(heatmapFile, 'w') as htmlFile:
	htmlFile.write(top + heatMapData + bottom)
