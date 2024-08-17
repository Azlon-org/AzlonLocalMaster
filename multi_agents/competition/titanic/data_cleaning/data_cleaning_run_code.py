def generated_code_function():
    
    import pandas as pd
    
    # Load the datasets
    train_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/train.csv'
    test_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/test.csv'
    
    train_df = pd.read_csv(train_data_path)
    test_df = pd.read_csv(test_data_path)
    
    # Display the first few rows of the training data
    pass
    
    # Display the first few rows of the test data
    pass
    
    
    # Get information about the training data
    pass
    
    # Get summary statistics of the training data
    pass
    
    # Get information about the test data
    pass
    
    # Get summary statistics of the test data
    pass
    
    
    # Check for missing values in the training data
    missing_train = train_df.isnull().sum()
    missing_train_percentage = (missing_train / len(train_df)) * 100
    
    pass
    
    # Check for missing values in the test data
    missing_test = test_df.isnull().sum()
    missing_test_percentage = (missing_test / len(test_df)) * 100
    
    pass
    
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Plot the distribution of the 'Survived' column
    plt.figure(figsize=(8, 6))
    sns.countplot(x='Survived', data=train_df)
    plt.title('Distribution of Survived')
    plt.xlabel('Survived')
    plt.ylabel('Count')
    pass
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
        pass
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
        
        pass
        plt.close()
    
    
    # Identify potential outliers using boxplots
    for feature in numerical_features:
        plt.figure(figsize=(8, 6))
        sns.boxplot(x=train_df[feature].dropna())
        plt.title(f'Boxplot of {feature}')
        plt.xlabel(feature)
        pass
        plt.close()
    
    
    # Calculate the correlation matrix
    numeric_columns = train_df.select_dtypes(include=['float64', 'int64']).columns
    correlation_matrix = train_df[numeric_columns].corr()
    
    # Plot the heatmap of the correlation matrix
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix')
    pass
    plt.close()
    
    
    numeric_columns = train_df.select_dtypes(include=['float64', 'int64']).columns
    correlation_matrix = train_df[numeric_columns].corr()
    


    
    import pandas as pd
    from sklearn.impute import SimpleImputer
    
    # Load the datasets
    train_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/train.csv'
    test_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/test.csv'
    
    train_df = pd.read_csv(train_data_path)
    test_df = pd.read_csv(test_data_path)
    
    # Copy the DataFrames before processing
    train_df_clean = train_df.copy()
    test_df_clean = test_df.copy()
    
    # Identify missing values
    missing_train = train_df_clean.isnull().sum()
    missing_test = test_df_clean.isnull().sum()
    
    print("Missing Values in Training Data:")
    print(missing_train)
    
    print("\nMissing Values in Test Data:")
    print(missing_test)
    
    # Handle missing values
    # For 'Age', 'Fare' columns, we will use the median to fill missing values
    imputer = SimpleImputer(strategy='median')
    train_df_clean['Age'] = imputer.fit_transform(train_df_clean[['Age']])
    test_df_clean['Age'] = imputer.transform(test_df_clean[['Age']])
    train_df_clean['Fare'] = imputer.fit_transform(train_df_clean[['Fare']])
    test_df_clean['Fare'] = imputer.transform(test_df_clean[['Fare']])
    
    # For 'Embarked' column, we will use the mode to fill missing values
    imputer = SimpleImputer(strategy='most_frequent')
    train_df_clean['Embarked'] = imputer.fit_transform(train_df_clean[['Embarked']]).ravel()
    test_df_clean['Embarked'] = imputer.transform(test_df_clean[['Embarked']]).ravel()
    
    # Drop 'Cabin' column due to too many missing values
    train_df_clean.drop(columns=['Cabin'], inplace=True)
    test_df_clean.drop(columns=['Cabin'], inplace=True)
    
    # Verify that there are no more missing values
    assert train_df_clean.isnull().sum().sum() == 0, "There are still missing values in the training data."
    assert test_df_clean.isnull().sum().sum() == 0, "There are still missing values in the test data."
    
    print("Missing values handled successfully.")
    
    
    # Handle incorrect or inconsistent data
    # Check for negative ages
    assert (train_df_clean['Age'] >= 0).all(), "There are negative ages in the training data."
    assert (test_df_clean['Age'] >= 0).all(), "There are negative ages in the test data."
    
    # Check for invalid ticket numbers (e.g., empty strings)
    assert train_df_clean['Ticket'].str.strip().astype(bool).all(), "There are invalid ticket numbers in the training data."
    assert test_df_clean['Ticket'].str.strip().astype(bool).all(), "There are invalid ticket numbers in the test data."
    
    print("No incorrect or inconsistent data found.")
    
    
    # Convert data types
    # Convert 'Pclass', 'SibSp', 'Parch' to categorical
    categorical_columns = ['Pclass', 'SibSp', 'Parch', 'Embarked', 'Sex']
    for col in categorical_columns:
        train_df_clean[col] = train_df_clean[col].astype('category')
        test_df_clean[col] = test_df_clean[col].astype('category')
    
    # Ensure numerical columns are of correct type
    numerical_columns = ['Age', 'Fare']
    for col in numerical_columns:
        train_df_clean[col] = train_df_clean[col].astype('float')
        test_df_clean[col] = test_df_clean[col].astype('float')
    
    # Verify data types
    for col in categorical_columns:
        assert train_df_clean[col].dtype == 'category', f"Column {col} is not of type 'category' in the training data."
        assert test_df_clean[col].dtype == 'category', f"Column {col} is not of type 'category' in the test data."
    for col in numerical_columns:
        assert train_df_clean[col].dtype == 'float64', f"Column {col} is not of type 'float' in the training data."
        assert test_df_clean[col].dtype == 'float64', f"Column {col} is not of type 'float' in the test data."
    
    print("Data types converted successfully.")
    
    
    # Standardize categorical variables
    # Ensure consistency in 'Embarked' column
    train_df_clean['Embarked'] = train_df_clean['Embarked'].str.strip().str.upper()
    test_df_clean['Embarked'] = test_df_clean['Embarked'].str.strip().str.upper()
    
    # Verify standardization
    assert train_df_clean['Embarked'].isin(['C', 'Q', 'S']).all(), "There are inconsistent values in the 'Embarked' column in the training data."
    assert test_df_clean['Embarked'].isin(['C', 'Q', 'S']).all(), "There are inconsistent values in the 'Embarked' column in the test data."
    
    print("Categorical variables standardized successfully.")
    
    
    # Remove duplicates
    train_df_clean.drop_duplicates(inplace=True)
    test_df_clean.drop_duplicates(inplace=True)
    
    # Verify no duplicates
    assert not train_df_clean.duplicated().any(), "There are duplicate rows in the training data."
    assert not test_df_clean.duplicated().any(), "There are duplicate rows in the test data."
    
    print("Duplicates removed successfully.")
    
    
    import numpy as np
    
    # Identify and handle outliers using IQR
    def handle_outliers(df, column):
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df[column] = np.where(df[column] < lower_bound, lower_bound, df[column])
        df[column] = np.where(df[column] > upper_bound, upper_bound, df[column])
    
    # Handle outliers in 'Age' and 'Fare' columns
    handle_outliers(train_df_clean, 'Age')
    handle_outliers(train_df_clean, 'Fare')
    handle_outliers(test_df_clean, 'Age')
    handle_outliers(test_df_clean, 'Fare')
    
    print("Outliers handled successfully.")
    
    
    # Save the cleaned data
    train_df_clean.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_train.csv', index=False)
    test_df_clean.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_test.csv', index=False)
    
    print("Cleaned data saved successfully.")
    


if __name__ == "__main__":
    generated_code_function()