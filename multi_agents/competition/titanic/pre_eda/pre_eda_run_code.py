def generated_code_function():
    
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Load the data
    train_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/train.csv'
    test_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/test.csv'
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    # Display the first few rows of each DataFrame
    print("Training Data:")
    print(train_df.head(10))
    print("\nTest Data:")
    print(test_df.head(10))
    
    # Examine the structure of the training data
    print("Training Data Info:")
    print(train_df.info())
    
    # Examine the structure of the test data
    print("Test Data Info:")
    print(test_df.info())
    
    # Check the shape of the DataFrames
    print(f"Training Data Shape: {train_df.shape}")
    print(f"Test Data Shape: {test_df.shape}")
    
    # Summarize basic statistics for numerical features in the training data
    print("Training Data Numerical Features Summary:")
    print(train_df.describe())
    
    # Summarize basic statistics for categorical features in the training data
    print("Training Data Categorical Features Summary:")
    print(train_df.describe(include=['O']))
    
    # Summarize basic statistics for numerical features in the test data
    print("Test Data Numerical Features Summary:")
    print(test_df.describe())
    
    # Summarize basic statistics for categorical features in the test data
    print("Test Data Categorical Features Summary:")
    print(test_df.describe(include=['O']))
    
    # Visualize distributions of numerical features in the training data
    numerical_features = ['Age', 'Fare', 'SibSp', 'Parch']
    for feature in numerical_features:
        plt.figure(figsize=(10, 6))
        sns.histplot(train_df[feature].dropna(), kde=True)
        plt.title(f'Distribution of {feature} in Training Data')
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/train_{feature}_distribution.png')
        plt.show()
    
    # Visualize distributions of categorical features in the training data
    categorical_features = ['Pclass', 'Sex', 'Embarked']
    for feature in categorical_features:
        plt.figure(figsize=(10, 6))
        sns.countplot(x=feature, data=train_df)
        plt.title(f'Distribution of {feature} in Training Data')
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/train_{feature}_distribution.png')
        plt.show()
    
    # Identify missing values in the training data
    print("Missing Values in Training Data:")
    print(train_df.isnull().sum())
    
    # Identify missing values in the test data
    print("Missing Values in Test Data:")
    print(test_df.isnull().sum())
    
    # Visualize missing values using a heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(train_df.isnull(), cbar=False, cmap='viridis')
    plt.title('Missing Values in Training Data')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/train_missing_values_heatmap.png')
    plt.show()
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(test_df.isnull(), cbar=False, cmap='viridis')
    plt.title('Missing Values in Test Data')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/test_missing_values_heatmap.png')
    plt.show()
    
    # Compute the correlation matrix for numerical features in the training data
    numeric_train_df = train_df.select_dtypes(include=['float64', 'int64'])
    correlation_matrix = numeric_train_df.corr()
    
    # Visualize the correlation matrix using a heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix of Numerical Features in Training Data')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/train_correlation_matrix.png')
    plt.show()
    


if __name__ == "__main__":
    generated_code_function()