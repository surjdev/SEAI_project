import pandas as pd
# import numpy as np
from pathlib import Path

BUFFER_PATH = Path("AI/raw_buffer.csv")

from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import train_test_split, GridSearchCV
import pickle

class SVD_method():
    buffer_dir = Path("AI/svd_results")
    buffer_model_path = [
        buffer_dir / "model.pkl", 
        buffer_dir / "model_plus.pkl"
    ]
    def __init__(self, data:pd.DataFrame):
        self.buffer_dir.mkdir(parents=True, exist_ok=True)
        self.data = self.prepare_data(data)
        self.all_books = self.data["book_id"].unique()
        self.model = self.load_model(self.data)
    
    def train(self, data:pd.DataFrame):
        def individual_train(data, rating_col):
            reader = Reader(rating_scale=(1, data[rating_col].max()))
            data = Dataset.load_from_df(data[['user_id', 'book_id', rating_col]], reader)
            
            param_grid = {
                "n_factors": [50, 100, 150],
                "lr_all": [0.002, 0.005, 0.01],
                "reg_all": [0.02, 0.1, 0.4],
                "n_epochs": [20, 30]
            }
            gs = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=3, n_jobs=-1)
            gs.fit(data)
            print(gs.best_score['rmse'])
            print(gs.best_params['rmse'])
            best_model = SVD(**gs.best_params['rmse'])
            best_model.fit(data.build_full_trainset())
            return best_model
        
        model = {}
        model["model_plus"] = individual_train(data, "book_rating_plus")
        data = data.dropna(subset="book_rating")
        model["model"] = individual_train(data, "book_rating")
        return model

    def recommend(self, user_id, n=10):
        predictions = {} 
        for model_name, model in self.model.items():
            rated_books = self.data[self.data['user_id'] == user_id]['book_id'].tolist()
            books_to_predict = [b for b in self.all_books if b not in rated_books]
            prediction = [model.predict(user_id, book_id) for book_id in books_to_predict]
            prediction = sorted(prediction, key=lambda x: x.est, reverse=True)
            prediction = prediction[:n]
            prediction = pd.DataFrame(prediction)
            prediction = prediction[["iid", "est"]]
            prediction = prediction.rename(columns={"iid": "book_id", "est": "rating"})
            prediction = prediction.round(decimals=2)
            predictions[model_name] = prediction
            
        return predictions

    def save_model(self, model):
        for path in self.buffer_model_path:
            with open(path, 'wb') as f:
                pickle.dump(model[path.name.split(".")[0]], f)

    def update(self, data:pd.DataFrame):
        try:
            self.data = self.prepare_data(data)
            self.model = self.train(self.data)
            self.save_model(self.model)
            return {"update_svd_method":"success"}
        except Exception as e:
            return {"update_svd_method":"failed", "error": str(e)}

    def load_model(self, data:pd.DataFrame):
        model = {}
        if all([path.exists() for path in self.buffer_model_path]):
            for path in self.buffer_model_path:
                with open(path, 'rb') as f:
                    model[path.name.split(".")[0]] = pickle.load(f)
        else:
            model = self.train(data)
            self.save_model(model)
        return model
            
    def prepare_data(self, data:pd.DataFrame, user_threshold=3):
        data.dropna(subset="book_rating_plus", inplace=True)
        user_counts = data["user_id"].value_counts()
        users_to_keep = user_counts[user_counts >= user_threshold].index
        data = data[data["user_id"].isin(users_to_keep)]
        return data

class Statisical_method():
    buffer_dir = Path("AI/statistical_results")
    buffer_recommendation_path = [
        buffer_dir / "most_popular.csv", 
        buffer_dir / "most_rated.csv",
        buffer_dir / "most_controversial.csv", 
    ]
    def __init__(self, data:pd.DataFrame):
        self.buffer_dir.mkdir(parents=True, exist_ok=True)
        data = self.prepare_data(data)
        self.df_recommend = self.load_data(data)
        
    def update(self, data:pd.DataFrame):
        try:
            data = self.prepare_data(data)
            self.df_recommend = self.pre_calculate_recommendation(data)
            self.update_buffer(self.df_recommend)
            return {"update_statistical_method":"success"}
        except Exception as e:
            return {"update_statistical_method":"failed", "error": str(e)}
    
        
    def load_data(self, data:pd.DataFrame):
        df_recommend = {}
        if all([path.exists() for path in self.buffer_recommendation_path]):
            for path in self.buffer_recommendation_path:
                df_recommend[path.name.split(".")[0]] = pd.read_csv(path)
        else:
            df_recommend = self.pre_calculate_recommendation(data)
            self.update_buffer(df_recommend)
        return df_recommend
    
    def update_buffer(self, df_recommend):
        for path in self.buffer_recommendation_path:
            df_recommend[path.name.split(".")[0]].to_csv(path, index=False)
        
    def prepare_data(self, data:pd.DataFrame):
        data.dropna(subset="book_rating", inplace=True)
        return data
        
    def pre_calculate_recommendation(self, data:pd.DataFrame):
        df_recommend = {}
        for method in self.calculate_recommendation():
            df_recommend[method] = self.calculate_recommendation()[method](data)
        return df_recommend
    
    def calculate_recommendation(self):
        def cal_popular(df):
            df = df.groupby('book_id')[['book_rating']].count().sort_values("book_rating", ascending=False)
            df = df.rename(columns={"book_rating":"count"})
            df = df.round(decimals=2)
            df.reset_index(drop=False, inplace = True)
            return df
        def cal_rating(df):
            df =  df.groupby('book_id')['book_rating'].agg(['count', 'mean'])
            df = df[df['count'] > 50].sort_values(by='mean', ascending=False).head(20)
            df.drop("count", axis=1, inplace = True)
            df = df.rename(columns={"mean":"average_rating"})
            df = df.round(decimals=2)
            df.reset_index(drop=False, inplace = True)
            return df
        
        def cal_controversial(df):
            df = df.groupby('book_id')[['book_rating']].std().sort_values("book_rating", ascending=False)
            df = df.rename(columns={"book_rating":"standard_deviation"})
            df = df.round(decimals=2)
            df.reset_index(drop=False, inplace = True)
            return df
        
        return {
            "most_popular": cal_popular,
            "most_rated": cal_rating,
            "most_controversial": cal_controversial
        }
        
    def recommend(self, limit=10):
        return {method: df.head(limit) for method, df in self.df_recommend.items()}

class Recommender:
    def __init__(self):
        data = self.load_data()
        self.method = {
            "svd": SVD_method(data),
            "statistical": Statisical_method(data)
        }
    
    def update(self):
        data = self.load_data()
        status = {}
        # update model
        for method_name in self.method:
            status.update(self.method[method_name].update(data))
        return status

    def load_data(self):
        data = pd.read_csv(BUFFER_PATH)
        data = self.prepare_data(data)
        return data

    def prepare_data(self, data:pd.DataFrame, fav_score =3):
        def add_fav_score(row):
            if row["is_favourite"] == True:
                if pd.isna(row["book_rating"]):
                    return 10
                else:
                    return row["book_rating"] + fav_score
            else:
                return row["book_rating"]
        data["book_rating_plus"] = data.apply(add_fav_score, axis=1)
        data["book_rating_plus"] = (data["book_rating_plus"]/data["book_rating_plus"].max())*10
        data.dropna(subset="book_rating_plus", inplace=True)
        return data

    def recommend(self, user_id, limit=10):
        if user_id is None:
            df_recommend = self.method["statistical"].recommend(limit)
        else:
            df_recommend = {}
            df_recommend.update(self.method["svd"].recommend(user_id, limit))
            df_recommend.update(self.method["statistical"].recommend(limit))
        return self.transform_data(df_recommend)
    
    def transform_data(self, data:dict):
        for method in data:
            data[method] = data[method].to_dict()
            data[method] = {column: list(data[method][column].values()) for column in data[method]}
        return data
    
if __name__ == "__main__":
    recommender = Recommender()
    results = recommender.recommend(1, 10)
    # print(results)
    for method in results:
        print(method)
        print(results[method])
        print("+" * 100)
        # break
    