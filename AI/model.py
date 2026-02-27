import pandas as pd
# import numpy as np
from pathlib import Path

BUFFER_PATH = Path("AI/raw_buffer.csv")

# from surprise import SVD, Dataset, Reader, accuracy
# from surprise.model_selection import train_test_split, GridSearchCV

# class SVD_method():
#     model_path = Path("model.pkl")
#     def __init__(self):
#         self.method = None
#         self.reader = None
#         self.data = None
#         self.trainset = None
#         self.testset = None
#         self.predictions = None
#         self.load_model()

#     def load_data(self, df):
#         self.reader = Reader(rating_scale=(1, 5))
#         self.data = Dataset.load_from_df(df, self.reader)

#     def train(self):
#         self.trainset, self.testset = train_test_split(self.data, test_size=0.2)
#         self.model = SVD()
#         self.model.fit(self.trainset)

#     def evaluate(self):
#         self.predictions = self.model.test(self.testset)
#         accuracy.rmse(self.predictions)

#     def recommend(self, user_id, n=10):
#         all_items = self.data.all_items()
#         user_items = self.trainset.ur[user_id]
#         items_to_predict = [item for item in all_items if item not in user_items]
#         predictions = [self.model.predict(user_id, item) for item in items_to_predict]
#         predictions.sort(key=lambda x: x.est, reverse=True)
#         return predictions[:n]

#     def save_model(self, path):
#         with open(path, 'wb') as f:
#             pickle.dump(self.model, f)

#     def load_model(self):
#         with open(path, 'rb') as f:
#             self.model = pickle.load(f)

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
            # "svd": SVD_method(data),
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
        data.dropna(subset="book_rating_plus", inplace=True)
        return data

    def recommend(self, user_id, limit=10):
        if user_id is None:
            df_recommend = self.method["statistical"].recommend(limit)
        else:
            df_recommend = {}
            # df_recommend.update(self.method["svd"].recommend(user_id, limit))
            df_recommend.update(self.method["statistical"].recommend(limit))
        return self.transform_data(df_recommend)
    
    def transform_data(self, data:dict):
        for method in data:
            data[method] = data[method].to_dict()
            data[method] = {column: list(data[method][column].values()) for column in data[method]}
        return data
    
if __name__ == "__main__":
    recommender = Recommender()
    results = recommender.recommend(None, 10)
    print(results)
    # for method in results:
    #     print(method)
    #     print(results[method])
    #     print("+" * 100)
        # break
    