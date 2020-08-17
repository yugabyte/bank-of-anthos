import os
import json

from flask import Flask
from flask import request
from flask import jsonify



from google.cloud import automl_v1beta1 as automl

# TODO: replace with your own project info
project_id = 'your-project'
compute_region = 'us-central1'
model_display_name = 'your-automl-model-name'

client = automl.TablesClient(project=project_id, region=compute_region)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def get_prediction():
    if request.method == 'POST':
        data = request.get_json()
        inputs = data['predict_json']
        response = client.predict(
            model_display_name=model_display_name,
            inputs=inputs,
            feature_importance=True,
        )
        
        class_lookup = {
            "0": "not_fraud",
            "1": "fraud"
        }
        
        return_json = {}
        
        for i in range(2):
            feat_list = [
                (column.feature_importance, column.column_display_name)
                for column in response.payload[i].tables.tables_model_column_info
            ]

            feature_importance = {}
            print(feat_list)

            for j in feat_list:
                feature_importance[j[1]] = j[0]
                
            sorted_importance = {k: v for k, v in sorted(feature_importance.items(), key=lambda item: item[1], reverse=True)[:5]}
                
            # Only return highest confidence score
            if response.payload[i].tables.score > 0.5:
                return_json[class_lookup[str(i)]] = {
                    "confidence_score": response.payload[i].tables.score,
                    "feature_importance": sorted_importance
                }

        return json.dumps(return_json)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))