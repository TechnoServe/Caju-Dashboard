#!/bin/bash

python3 manage.py migrate --skip-checks

python3 ./staticfiles/well_i_dont_know_their_use/import_alteia_data.py
python3 ./staticfiles/well_i_dont_know_their_use/import_nurseries.py
python3 ./staticfiles/well_i_dont_know_their_use/import_plantations.py
python3 ./staticfiles/well_i_dont_know_their_use/import_satellite_data.py
python3 ./staticfiles/well_i_dont_know_their_use/Import_training_dummy_data.py

cp ./apps/dashboard/scripts/build_satellite_prediction_computed_data.py . && python3 build_satellite_prediction_computed_data.py && rm build_satellite_prediction_computed_data.py

python3 ./apps/dashboard/scripts/tree_spacing_recommandations.py
