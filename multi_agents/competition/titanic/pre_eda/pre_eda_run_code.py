def generated_code_function():
    
    import pandas as pd
    
    # Load the datasets
    train_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/train.csv'
    test_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/test.csv'
    
    train_df = pd.read_csv(train_data_path)
    test_df = pd.read_csv(test_data_path)
    
    # Display the first few rows of the training data
    print("Training Data:")
    print(train_df.head())
    
    # Display the first few rows of the test data
    print("\nTest Data:")
    print(test_df.head())
    
    
    # Get information about the training data
    print("Training Data Info:")
    print(train_df.info())
    
    # Get summary statistics of the training data
    print("\nTraining Data Summary Statistics:")
    print(train_df.describe(include='all'))
    
    # Get information about the test data
    print("\nTest Data Info:")
    print(test_df.info())
    
    # Get summary statistics of the test data
    print("\nTest Data Summary Statistics:")
    print(test_df.describe(include='all'))
    
    
    # Check for missing values in the training data
    missing_train = train_df.isnull().sum()
    missing_train_percentage = (missing_train / len(train_df)) * 100
    
    print("Missing Values in Training Data:")
    print(missing_train_percentage)
    
    # Check for missing values in the test data
    missing_test = test_df.isnull().sum()
    missing_test_percentage = (missing_test / len(test_df)) * 100
    
    print("\nMissing Values in Test Data:")
    print(missing_test_percentage)
    
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Plot the distribution of the 'Survived' column
    plt.figure(figsize=(8, 6))
    sns.countplot(x='Survived', data=train_df)
    plt.title('Distribution of Survived')
    plt.xlabel('Survived')
    plt.ylabel('Count')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/distribution_of_survived.png')
    plt.close()
    
    
    # List of categorical features
    categorical_features = ['Pclass', 'Sex', 'SibSp', 'Parch', 'Embarked']
    
    # Plot the distribution of each categorical feature
    for feature in categorical_features:
        plt.figure(figsize=(8, 6))
        sns.countplot(x=feature, data=train_df)
        plt.title(f'Distribution of {feature}')
        plt.xlabel(feature)
        plt.ylabel('Count')
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/distribution_of_{feature}.png')
        plt.close()
    
    
    # List of numerical features
    numerical_features = ['Age', 'Fare']
    
    # Plot histograms and boxplots for each numerical feature
    for feature in numerical_features:
        plt.figure(figsize=(12, 6))
        
        # Histogram
        plt.subplot(1, 2, 1)
        sns.histplot(train_df[feature].dropna(), kde=True)
        plt.title(f'Histogram of {feature}')
        plt.xlabel(feature)
        plt.ylabel('Frequency')
        
        # Boxplot
        plt.subplot(1, 2, 2)
        sns.boxplot(x=train_df[feature].dropna())
        plt.title(f'Boxplot of {feature}')
        plt.xlabel(feature)
        
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/{feature}_distribution.png')
        plt.close()
    
    
    # Identify potential outliers using boxplots
    for feature in numerical_features:
        plt.figure(figsize=(8, 6))
        sns.boxplot(x=train_df[feature].dropna())
        plt.title(f'Boxplot of {feature}')
        plt.xlabel(feature)
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/{feature}_outliers.png')
        plt.close()
    
    
    # Calculate the correlation matrix
    numeric_columns = train_df.select_dtypes(include=['float64', 'int64']).columns
    correlation_matrix = train_df[numeric_columns].corr()
    
    # Plot the heatmap of the correlation matrix
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/correlation_matrix.png')
    plt.close()
    
    
    numeric_columns = train_df.select_dtypes(include=['float64', 'int64']).columns
    correlation_matrix = train_df[numeric_columns].corr()
    


if __name__ == "__main__":
    generated_code_function()