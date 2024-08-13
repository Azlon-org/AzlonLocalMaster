def generated_code_function():
    
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Load the data
    train_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/train.csv'
    test_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/test.csv'
    
    train_df = pd.read_csv(train_data_path)
    test_df = pd.read_csv(test_data_path)
    
    # Verify the data loading
    print(train_df.head(10))
    print(test_df.head(10))
    
    # Understand the data structure
    print(train_df.info())
    print(train_df.head())
    
    print(test_df.info())
    print(test_df.head())
    
    # Summary statistics for numerical features
    print(train_df.describe())
    
    # Summary statistics for categorical features
    print(train_df.describe(include=['O']))
    
    # Check for missing values
    print(train_df.isnull().sum())
    print(test_df.isnull().sum())
    
    # Histograms for numerical features
    numerical_features = ['Age', 'Fare', 'SibSp', 'Parch']
    for feature in numerical_features:
        plt.figure(figsize=(10, 6))
        sns.histplot(train_df[feature].dropna(), kde=True)
        plt.title(f'Histogram of {feature}')
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/histogram_{feature}.png')
        plt.show()
    
    # Count plots for categorical features
    categorical_features = ['Pclass', 'Sex', 'Embarked']
    for feature in categorical_features:
        plt.figure(figsize=(10, 6))
        sns.countplot(x=feature, data=train_df)
        plt.title(f'Count Plot of {feature}')
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/countplot_{feature}.png')
        plt.show()
    
    # Correlation analysis
    numeric_columns = train_df.select_dtypes(include=['number']).columns
    correlation_matrix = train_df[numeric_columns].corr()
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/correlation_matrix.png')
    plt.show()
    
    # Initial observations
    observations = """
    1. There are missing values in the 'Age', 'Cabin', and 'Embarked' columns in the training dataset.
    2. The 'Fare' column has a wide range of values, indicating potential outliers.
    3. The 'Survived' column is the target variable with binary values (0 and 1).
    4. The 'Pclass' column is a categorical feature with three unique values (1, 2, 3).
    5. The 'Sex' column is a categorical feature with two unique values (male, female).
    6. The 'Embarked' column has three unique values (C, Q, S) but also contains missing values.
    7. The correlation matrix shows that 'Pclass' and 'Fare' have a moderate negative correlation.
    """
    
    print(observations)
    
    
    numeric_columns = train_df.select_dtypes(include=['number']).columns
    correlation_matrix = train_df[numeric_columns].corr()
    


if __name__ == "__main__":
    generated_code_function()