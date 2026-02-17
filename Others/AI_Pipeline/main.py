from pathlib import Path
import pandas as pd
from abc import ABC, abstractmethod
from sklearn.base import BaseEstimator
import joblib

class AI_Pipeline(ABC):
    """
    This class is the main class for the AI pipeline.
    It is the main class for the AI pipeline.
    """

    models_dir=Path("Others/AI_Pipeline/models")

    def __init__(self, model_name:str, model:BaseEstimator):
        self.model_name:str=model_name
        self.model:BaseEstimator=model
        
        self.create_models_dir()

    def create_models_dir(self):
        """
        Create the directory for the model.
        """
        (self.models_dir/self.model_name).mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def load_data(self, data_path:Path) -> pd.DataFrame:
        """
        Load the data from the given path.
        """
        pass

    @abstractmethod
    def preprocess_data(self, data:pd.DataFrame) -> dict:
        """
        Preprocess the data.
        """
        pass

    @abstractmethod
    def train_model(self, preprocessed_data:dict) -> BaseEstimator:
        """
        Train the model.
        """
        pass

    @abstractmethod
    def evaluate_model(self, trained_model:BaseEstimator, preprocessed_data:dict) -> dict:
        """
        Evaluate the model.
        """
        pass

    @abstractmethod
    def save_model(self, trained_model:BaseEstimator, eval_results:dict) -> None:
        """
        Save the model.
        """
        pass

    def run(self):
        """
        Run the AI pipeline.
        """
        data = self.load_data()
        preprocessed_data = self.preprocess_data(data)
        trained_model = self.train_model(preprocessed_data)
        eval_results = self.evaluate_model(trained_model, preprocessed_data)
        self.save_model(trained_model, eval_results)

class Test_Pipeline(AI_Pipeline):
    def __init__(self, model_name, model):
        super().__init__(model_name, model)

    def load_data(self, data_path:Path) -> pd.DataFrame:
        data = pd.read_csv(data_path)
        return data

    def preprocess_data(self, data:pd.DataFrame, test_size:float=0.2, random_state:int=42) -> dict:
        X_train, X_test, y_train, y_test = train_test_split(data.drop("target", axis=1), data["target"], test_size=test_size, random_state=random_state)
        preprocessed_data = {
            "X_train":X_train,
            "y_train":y_train,
            "X_test":X_test,
            "y_test":y_test
        }
        return preprocessed_data
        
    def train_model(self, preprocessed_data:dict) -> BaseEstimator:
        self.model.fit(preprocessed_data["X_train"], preprocessed_data["y_train"])
        return self.model

    def evaluate_model(self, trained_model:BaseEstimator, preprocessed_data:dict) -> dict:
        y_pred = trained_model.predict(preprocessed_data["X_test"])
        eval_results = {}
        if not eval_results:
            raise ValueError("Evaluation results are empty.")
        return eval_results

    def save_model(self, trained_model:BaseEstimator, eval_results:dict) -> None:
        joblib.dump(trained_model, self.models_dir/self.model_name/f"{self.model_name}.pkl")
        joblib.dump(eval_results, self.models_dir/self.model_name/f"{self.model_name}_eval_results.pkl")

def main() -> None:
    model = KNeighborsClassifier()
    pipeline = Test_Pipeline(model_name="Test", model=model)
    pipeline.run()

if __name__ == "__main__":
    main()