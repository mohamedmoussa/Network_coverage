from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
from coverage_data import NetworkCoverage
from flask_caching import Cache
import logging

app = Flask(__name__)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
geolocator = Nominatim(user_agent="network_coverage_api")
coverage = NetworkCoverage('2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv')
logging.basicConfig(level=logging.INFO)


@app.route('/api/network_coverage', methods=['GET'])
def network_coverage():
    address = request.args.get('q')
    if not address:
        return jsonify({"error": "Paramètre 'q' manquant"}), 400
    location = cache.get(f"geocode:{address}")
    if location is None:
        try:
            geo_location = geolocator.geocode(address, timeout=10)
            if geo_location:
                location = (geo_location.latitude, geo_location.longitude)
                cache.set(f"geocode:{address}", location, timeout=86400)
            else:
                location = None
        except Exception as e:
            app.logger.error(f"Erreur de géocodage : {e}")
            return jsonify({"error": "Erreur du service de géocodage"}), 500
    if location:
        latitude, longitude = location
        result = coverage.get_coverage(latitude, longitude)
        return jsonify(result)
    else:
        return jsonify({"error": "Adresse non trouvée"}), 404


if __name__ == '__main__':
    app.run(debug=True)