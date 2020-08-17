# ML demo code

This is the code for the data + machine learning portion of the Bank of Anthos demo. We used a credit card fraud detection dataset to train the model, available in BigQuery public datasets (shown below) and on [Kaggle](https://www.kaggle.com/mlg-ulb/creditcardfraud). In the demo we made up new column names, here we're using the originals (V1, V2, etc.).

This code was tested from a [Cloud AI Platform Notebooks](https://cloud.google.com/ai-platform-notebooks) instance - we recommend you run it there.

## Data preprocessing

The `fraud_data_preprocessing.ipynb` notebook in the root directory here shows how to perform [downsampling](https://developers.google.com/machine-learning/data-prep/construct/sampling-splitting/imbalanced-data#downsampling-and-upweighting) and write the updated dataset to a new BigQuery table. 

After running this notebook, use the AutoML Tables UI to train and deploy your model. If you've never done that before, check out the [docs](https://cloud.google.com/automl-tables/docs/import).

## Getting a prediction from a notebook

Once you've trained an AutoML Tables model, get a test prediction by running the `automl_predict.ipynb` notebook.

## Creating a Cloud Run service

To create a [Cloud Run](https://cloud.google.com/run) service for pinging your deployed model, first open a Terminal window from Cloud AI Platform Notebooks and `cd` into the `cloudrun/` directory. Go into `app.py` and update the variables at the top of the file with the name of your Google Cloud project and AutoML Tables deploeyd model. Then, run the following, updated with the name of your project and the name you'd like to use for your Cloud Run service:

```
gcloud builds submit --tag gcr.io/your-project/your_service_name
```

Then run:

```
gcloud run deploy --image gcr.io/your-project/your_service_name --platform managed
```

Once your service is deployed, take note of the URL of your new service. You can navigate to the Cloud Run UI in your Cloud console to confirm it deployed correctly. Then, change the authentication on your service to "Allow unauthenticated." 

To test out your service, make a request to it via curl. Update the following with the URL of your Cloud Run service:

```
curl -H "Content-Type: application/json" --request POST --data @test.json https://your-cloud-run-url.app | jq "."
```