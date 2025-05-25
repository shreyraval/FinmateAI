from sklearn.cluster import KMeans

def classify_transactions(df):
    # Add your logic here or a pretrained model
    df['Category'] = ...
    return df.to_dict(orient="records")
