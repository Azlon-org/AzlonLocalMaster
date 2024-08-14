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
    
    # Understand the data structure
    
    
    # Summary statistics for numerical features
    
    # Summary statistics for categorical features
    
    # Check for missing values
    
    # Histograms for numerical features
    numerical_features = ['Age', 'Fare', 'SibSp', 'Parch']
    for feature in numerical_features:
        plt.figure(figsize=(10, 6))
        sns.histplot(train_df[feature].dropna(), kde=True)
        plt.title(f'Histogram of {feature}')
    
    # Count plots for categorical features
    categorical_features = ['Pclass', 'Sex', 'Embarked']
    for feature in categorical_features:
        plt.figure(figsize=(10, 6))
        sns.countplot(x=feature, data=train_df)
        plt.title(f'Count Plot of {feature}')
    
    # Correlation analysis
    numeric_columns = train_df.select_dtypes(include=['number']).columns
    correlation_matrix = train_df[numeric_columns].corr()
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix')
    
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
    
    
    
    numeric_columns = train_df.select_dtypes(include=['number']).columns
    correlation_matrix = train_df[numeric_columns].corr()
    


    
    # Identify Missing Values
    missing_values_train = train_df.isnull().sum()
    missing_values_test = test_df.isnull().sum()
    
    print("Missing values in training data:\n", missing_values_train)
    print("Missing values in test data:\n", missing_values_test)
    
    
    # Handle Missing Values
    
    # For numerical features in training data
    train_df['Age'].fillna(train_df['Age'].median(), inplace=True)
    train_df['Fare'].fillna(train_df['Fare'].median(), inplace=True)
    
    # For categorical features in training data
    train_df['Embarked'].fillna(train_df['Embarked'].mode()[0], inplace=True)
    train_df['Cabin'].fillna('Unknown', inplace=True)
    
    # For numerical features in test data
    test_df['Age'].fillna(test_df['Age'].median(), inplace=True)
    test_df['Fare'].fillna(test_df['Fare'].median(), inplace=True)
    
    # For categorical features in test data
    test_df['Embarked'].fillna(test_df['Embarked'].mode()[0], inplace=True)
    test_df['Cabin'].fillna('Unknown', inplace=True)
    
    # Verify missing values are handled
    print("Missing values in training data after imputation:\n", train_df.isnull().sum())
    print("Missing values in test data after imputation:\n", test_df.isnull().sum())
    
    
    # Correct Data Types
    
    # Convert 'Pclass' to categorical
    train_df['Pclass'] = train_df['Pclass'].astype('category')
    test_df['Pclass'] = test_df['Pclass'].astype('category')
    
    # Verify data types
    print(train_df.dtypes)
    print(test_df.dtypes)
    
    
    # Address Inconsistencies and Errors
    
    # Check for and handle duplicate rows
    train_df.drop_duplicates(inplace=True)
    test_df.drop_duplicates(inplace=True)
    
    # Validate ranges and categories for each feature
    assert train_df['Age'].between(0, 100).all(), "Age values are out of range"
    assert train_df['Fare'].between(0, 600).all(), "Fare values are out of range"
    assert set(train_df['Pclass'].unique()).issubset({1, 2, 3}), "Pclass values are incorrect"
    assert set(train_df['Sex'].unique()).issubset({'male', 'female'}), "Sex values are incorrect"
    assert set(train_df['Embarked'].unique()).issubset({'C', 'Q', 'S'}), "Embarked values are incorrect"
    
    # Verify no duplicates
    print("Duplicates in training data:", train_df.duplicated().sum())
    print("Duplicates in test data:", test_df.duplicated().sum())
    
    
    # Feature-Specific Cleaning
    
    # For the 'Age' column: Consider creating age bins if the distribution is highly skewed
    train_df['AgeBin'] = pd.cut(train_df['Age'], bins=[0, 12, 20, 40, 60, 80, 100], labels=['Child', 'Teen', 'Adult', 'Middle-Aged', 'Senior', 'Elderly'])
    test_df['AgeBin'] = pd.cut(test_df['Age'], bins=[0, 12, 20, 40, 60, 80, 100], labels=['Child', 'Teen', 'Adult', 'Middle-Aged', 'Senior', 'Elderly'])
    
    # For the 'Fare' column: Handle any outliers or zero values appropriately
    train_df['Fare'] = train_df['Fare'].replace(0, train_df['Fare'].median())
    test_df['Fare'] = test_df['Fare'].replace(0, test_df['Fare'].median())
    
    # For the 'Cabin' column: Extract deck information if useful and handle missing values
    train_df['Deck'] = train_df['Cabin'].str[0]
    test_df['Deck'] = test_df['Cabin'].str[0]
    
    # For the 'Embarked' column: Impute missing values with the most frequent port of embarkation (already done)
    
    # Verify feature-specific cleaning
    print(train_df[['Age', 'AgeBin', 'Fare', 'Cabin', 'Deck']].head())
    print(test_df[['Age', 'AgeBin', 'Fare', 'Cabin', 'Deck']].head())
    
    
    # Ensure Data Consistency
    
    # Final check using .info() and .head()
    print(train_df.info())
    print(train_df.head())
    
    print(test_df.info())
    print(test_df.head())
    
    
    # Document Cleaning Process
    
    cleaning_log = """
    1. Identified missing values in 'Age', 'Cabin', and 'Embarked' columns.
    2. Imputed missing values in 'Age' and 'Fare' columns with the median.
    3. Imputed missing values in 'Embarked' column with the most frequent value.
    4. Filled missing values in 'Cabin' column with 'Unknown'.
    5. Converted 'Pclass' column to categorical data type.
    6. Removed duplicate rows.
    7. Validated ranges and categories for each feature.
    8. Created age bins for 'Age' column.
    9. Replaced zero values in 'Fare' column with the median.
    10. Extracted deck information from 'Cabin' column.
    11. Performed final check to ensure data consistency.
    """
    
    print(cleaning_log)
    
    
    # Save Cleaned Data
    train_df.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_train.csv', index=False)
    test_df.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_test.csv', index=False)
    
    
    import pandas as pd
    
    # Load the data
    train_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/train.csv'
    test_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/test.csv'
    
    train_df = pd.read_csv(train_data_path)
    test_df = pd.read_csv(test_data_path)
    
    # Identify Missing Values
    missing_values_train = train_df.isnull().sum()
    missing_values_test = test_df.isnull().sum()
    
    print("Missing values in training data:\n", missing_values_train)
    print("Missing values in test data:\n", missing_values_test)
    
    # Handle Missing Values
    train_df['Age'].fillna(train_df['Age'].median(), inplace=True)
    train_df['Fare'].fillna(train_df['Fare'].median(), inplace=True)
    train_df['Embarked'].fillna(train_df['Embarked'].mode()[0], inplace=True)
    train_df['Cabin'].fillna('Unknown', inplace=True)
    
    test_df['Age'].fillna(test_df['Age'].median(), inplace=True)
    test_df['Fare'].fillna(test_df['Fare'].median(), inplace=True)
    test_df['Embarked'].fillna(test_df['Embarked'].mode()[0], inplace=True)
    test_df['Cabin'].fillna('Unknown', inplace=True)
    
    print("Missing values in training data after imputation:\n", train_df.isnull().sum())
    print("Missing values in test data after imputation:\n", test_df.isnull().sum())
    
    # Correct Data Types
    train_df['Pclass'] = train_df['Pclass'].astype('category')
    test_df['Pclass'] = test_df['Pclass'].astype('category')
    
    print(train_df.dtypes)
    print(test_df.dtypes)
    
    # Address Inconsistencies and Errors
    train_df.drop_duplicates(inplace=True)
    test_df.drop_duplicates(inplace=True)
    
    assert train_df['Age'].between(0, 100).all(), "Age values are out of range"
    assert train_df['Fare'].between(0, 600).all(), "Fare values are out of range"
    assert set(train_df['Pclass'].unique()).issubset({1, 2, 3}), "Pclass values are incorrect"
    assert set(train_df['Sex'].unique()).issubset({'male', 'female'}), "Sex values are incorrect"
    assert set(train_df['Embarked'].unique()).issubset({'C', 'Q', 'S'}), "Embarked values are incorrect"
    
    print("Duplicates in training data:", train_df.duplicated().sum())
    print("Duplicates in test data:", test_df.duplicated().sum())
    
    # Feature-Specific Cleaning
    train_df['AgeBin'] = pd.cut(train_df['Age'], bins=[0, 12, 20, 40, 60, 80, 100], labels=['Child', 'Teen', 'Adult', 'Middle-Aged', 'Senior', 'Elderly'])
    test_df['AgeBin'] = pd.cut(test_df['Age'], bins=[0, 12, 20, 40, 60, 80, 100], labels=['Child', 'Teen', 'Adult', 'Middle-Aged', 'Senior', 'Elderly'])
    
    train_df['Fare'] = train_df['Fare'].replace(0, train_df['Fare'].median())
    test_df['Fare'] = test_df['Fare'].replace(0, test_df['Fare'].median())
    
    train_df['Deck'] = train_df['Cabin'].str[0]
    test_df['Deck'] = test_df['Cabin'].str[0]
    
    print(train_df[['Age', 'AgeBin', 'Fare', 'Cabin', 'Deck']].head())
    print(test_df[['Age', 'AgeBin', 'Fare', 'Cabin', 'Deck']].head())
    
    # Ensure Data Consistency
    print(train_df.info())
    print(train_df.head())
    
    print(test_df.info())
    print(test_df.head())
    
    # Document Cleaning Process
    cleaning_log = """
    1. Identified missing values in 'Age', 'Cabin', and 'Embarked' columns.
    2. Imputed missing values in 'Age' and 'Fare' columns with the median.
    3. Imputed missing values in 'Embarked' column with the most frequent value.
    4. Filled missing values in 'Cabin' column with 'Unknown'.
    5. Converted 'Pclass' column to categorical data type.
    6. Removed duplicate rows.
    7. Validated ranges and categories for each feature.
    8. Created age bins for 'Age' column.
    9. Replaced zero values in 'Fare' column with the median.
    10. Extracted deck information from 'Cabin' column.
    11. Performed final check to ensure data consistency.
    """
    
    print(cleaning_log)
    
    # Save Cleaned Data
    train_df.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_train.csv', index=False)
    test_df.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_test.csv', index=False)
    


if __name__ == "__main__":
    generated_code_function()