import spacy


class SpacyPredictor(object):
    """Interface for constructing custom predictors."""

    def __init__(self, model):
        self.model = model

    def predict(self, instances, **kwargs):
        """Performs custom prediction.

        Instances are the decoded values from the request. They have already
        been deserialized from JSON.

        Args:
            instances: A list of prediction input instances.
            **kwargs: A dictionary of keyword args provided as additional
                fields on the predict request body.

        Returns:
            A list of outputs containing the prediction results. This list must
            be JSON serializable.
        """
        errors = []
        for instance in instances:
            doc = self.model(instance)
            errors.append(doc.ents)

        return errors

    @classmethod
    def from_path(cls, model_dir):
        """Creates an instance of Predictor using the given path.

        Loading of the predictor should be done in this method.

        Args:
            model_dir: The local directory that contains the exported model
                file along with any additional files uploaded when creating the
                version resource.

        Returns:
            An instance implementing this Predictor class.
        """
        model = spacy.load(model_dir)
        return cls(model)