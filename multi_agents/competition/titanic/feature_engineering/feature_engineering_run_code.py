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
    
    pass
    
    pass
    
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
    
    pass
    
    
    # Handle incorrect or inconsistent data
    # Check for negative ages
    assert (train_df_clean['Age'] >= 0).all(), "There are negative ages in the training data."
    assert (test_df_clean['Age'] >= 0).all(), "There are negative ages in the test data."
    
    # Check for invalid ticket numbers (e.g., empty strings)
    assert train_df_clean['Ticket'].str.strip().astype(bool).all(), "There are invalid ticket numbers in the training data."
    assert test_df_clean['Ticket'].str.strip().astype(bool).all(), "There are invalid ticket numbers in the test data."
    
    pass
    
    
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
    
    pass
    
    
    # Standardize categorical variables
    # Ensure consistency in 'Embarked' column
    train_df_clean['Embarked'] = train_df_clean['Embarked'].str.strip().str.upper()
    test_df_clean['Embarked'] = test_df_clean['Embarked'].str.strip().str.upper()
    
    # Verify standardization
    assert train_df_clean['Embarked'].isin(['C', 'Q', 'S']).all(), "There are inconsistent values in the 'Embarked' column in the training data."
    assert test_df_clean['Embarked'].isin(['C', 'Q', 'S']).all(), "There are inconsistent values in the 'Embarked' column in the test data."
    
    pass
    
    
    # Remove duplicates
    train_df_clean.drop_duplicates(inplace=True)
    test_df_clean.drop_duplicates(inplace=True)
    
    # Verify no duplicates
    assert not train_df_clean.duplicated().any(), "There are duplicate rows in the training data."
    assert not test_df_clean.duplicated().any(), "There are duplicate rows in the test data."
    
    pass
    
    
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
    
    pass
    
    
    # Save the cleaned data
    train_df_clean.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_train.csv', index=False)
    test_df_clean.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_test.csv', index=False)
    
    pass
    


    
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    import scipy.stats as stats
    
    # Load the cleaned datasets
    train_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_train.csv'
    test_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_test.csv'
    
    train_df = pd.read_csv(train_data_path)
    test_df = pd.read_csv(test_data_path)
    
    # Display the first few rows of the cleaned training data
    pass
    
    # Display the first few rows of the cleaned test data
    pass
    
    # Ensure data types are correct
    assert train_df['Pclass'].dtype == 'int64', "Pclass should be of type int64"
    assert train_df['Survived'].dtype == 'int64', "Survived should be of type int64"
    assert train_df['Age'].dtype == 'float64', "Age should be of type float64"
    assert train_df['Fare'].dtype == 'float64', "Fare should be of type float64"
    
    # Visualize the relationship between 'Pclass' and 'Survived'
    plt.figure(figsize=(8, 6))
    sns.countplot(x='Pclass', hue='Survived', data=train_df)
    plt.title('Survival Count by Pclass')
    plt.xlabel('Pclass')
    plt.ylabel('Count')
    pass
    plt.close()
    
    # Visualize the relationship between 'Sex' and 'Survived'
    plt.figure(figsize=(8, 6))
    sns.countplot(x='Sex', hue='Survived', data=train_df)
    plt.title('Survival Count by Sex')
    plt.xlabel('Sex')
    plt.ylabel('Count')
    pass
    plt.close()
    
    # Visualize the relationship between 'Age' and 'Survived'
    plt.figure(figsize=(8, 6))
    sns.histplot(data=train_df, x='Age', hue='Survived', multiple='stack', kde=True)
    plt.title('Survival Distribution by Age')
    plt.xlabel('Age')
    plt.ylabel('Count')
    pass
    plt.close()
    
    # Visualize the relationship between 'Fare' and 'Survived'
    plt.figure(figsize=(8, 6))
    sns.histplot(data=train_df, x='Fare', hue='Survived', multiple='stack', kde=True)
    plt.title('Survival Distribution by Fare')
    plt.xlabel('Fare')
    plt.ylabel('Count')
    pass
    plt.close()
    
    # Visualize the relationship between 'Embarked' and 'Survived'
    plt.figure(figsize=(8, 6))
    sns.countplot(x='Embarked', hue='Survived', data=train_df)
    plt.title('Survival Count by Embarked')
    plt.xlabel('Embarked')
    plt.ylabel('Count')
    pass
    plt.close()
    
    # Perform statistical tests
    # Chi-square test for categorical variables
    def chi_square_test(feature):
        contingency_table = pd.crosstab(train_df[feature], train_df['Survived'])
        chi2, p, dof, expected = stats.chi2_contingency(contingency_table)
        return p
    
    categorical_features = ['Pclass', 'Sex', 'SibSp', 'Parch', 'Embarked']
    for feature in categorical_features:
        p_value = chi_square_test(feature)
        pass
    
    # T-test for numerical variables
    def t_test(feature):
        survived = train_df[train_df['Survived'] == 1][feature]
        not_survived = train_df[train_df['Survived'] == 0][feature]
        t_stat, p = stats.ttest_ind(survived, not_survived, nan_policy='omit')
        return p
    
    numerical_features = ['Age', 'Fare']
    for feature in numerical_features:
        p_value = t_test(feature)
        pass
    
    # Correlation analysis
    numeric_columns = train_df.select_dtypes(include=['float64', 'int64']).columns
    correlation_matrix = train_df[numeric_columns].corr()
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix')
    pass
    plt.close()
    
    # Visualize interaction between 'Pclass' and 'Sex' on 'Survived'
    plt.figure(figsize=(8, 6))
    sns.catplot(x='Pclass', hue='Sex', col='Survived', data=train_df, kind='count', height=5, aspect=1)
    pass
    plt.close()
    
    # Visualize interaction between 'Pclass' and 'Embarked' on 'Survived'
    plt.figure(figsize=(8, 6))
    sns.catplot(x='Pclass', hue='Embarked', col='Survived', data=train_df, kind='count', height=5, aspect=1)
    pass
    plt.close()
    
    # Visualize interaction between 'Sex' and 'Embarked' on 'Survived'
    plt.figure(figsize=(8, 6))
    sns.catplot(x='Sex', hue='Embarked', col='Survived', data=train_df, kind='count', height=5, aspect=1)
    pass
    plt.close()
    
    # Visualize interaction between 'SibSp' and 'Parch' on 'Survived'
    plt.figure(figsize=(8, 6))
    sns.catplot(x='SibSp', hue='Parch', col='Survived', data=train_df, kind='count', height=5, aspect=1)
    pass
    plt.close()
    


    
    import pandas as pd
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
    
    # Load the cleaned datasets
    train_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_train.csv'
    test_data_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/cleaned_test.csv'
    
    train_df = pd.read_csv(train_data_path)
    test_df = pd.read_csv(test_data_path)
    
    # Copy the DataFrames before processing
    train_df_fe = train_df.copy()
    test_df_fe = test_df.copy()
    
    # Create FamilySize feature
    train_df_fe['FamilySize'] = train_df_fe['SibSp'] + train_df_fe['Parch'] + 1
    test_df_fe['FamilySize'] = test_df_fe['SibSp'] + test_df_fe['Parch'] + 1
    
    # Create IsAlone feature
    train_df_fe['IsAlone'] = (train_df_fe['FamilySize'] == 1).astype(int)
    test_df_fe['IsAlone'] = (test_df_fe['FamilySize'] == 1).astype(int)
    
    # Extract Title from Name
    train_df_fe['Title'] = train_df_fe['Name'].str.extract(' ([A-Za-z]+)\.', expand=False)
    test_df_fe['Title'] = test_df_fe['Name'].str.extract(' ([A-Za-z]+)\.', expand=False)
    
    # Impute missing values for Age, Fare, Embarked
    imputer_median = SimpleImputer(strategy='median')
    imputer_mode = SimpleImputer(strategy='most_frequent')
    
    train_df_fe['Age'] = imputer_median.fit_transform(train_df_fe[['Age']])
    test_df_fe['Age'] = imputer_median.transform(test_df_fe[['Age']])
    
    train_df_fe['Fare'] = imputer_median.fit_transform(train_df_fe[['Fare']])
    test_df_fe['Fare'] = imputer_median.transform(test_df_fe[['Fare']])
    
    train_df_fe['Embarked'] = imputer_mode.fit_transform(train_df_fe[['Embarked']]).ravel()
    test_df_fe['Embarked'] = imputer_mode.transform(test_df_fe[['Embarked']]).ravel()
    
    # Verify that there are no more missing values
    assert train_df_fe.isnull().sum().sum() == 0, "There are still missing values in the training data."
    assert test_df_fe.isnull().sum().sum() == 0, "There are still missing values in the test data."
    
    print("Missing values handled successfully.")
    
    # Label Encoding for Pclass
    label_encoder = LabelEncoder()
    train_df_fe['Pclass'] = label_encoder.fit_transform(train_df_fe['Pclass'])
    test_df_fe['Pclass'] = label_encoder.transform(test_df_fe['Pclass'])
    
    # One-Hot Encoding for Sex, Embarked, Title
    train_df_fe = pd.get_dummies(train_df_fe, columns=['Sex', 'Embarked', 'Title'], drop_first=True)
    test_df_fe = pd.get_dummies(test_df_fe, columns=['Sex', 'Embarked', 'Title'], drop_first=True)
    
    # Ensure both train and test sets have the same columns after encoding
    missing_cols = set(train_df_fe.columns) - set(test_df_fe.columns)
    for col in missing_cols:
        test_df_fe[col] = 0
    test_df_fe = test_df_fe[train_df_fe.columns]
    
    # Display the first few rows to verify the encoding
    print("Training Data with Encoded Features:")
    print(train_df_fe.head())
    
    print("\nTest Data with Encoded Features:")
    print(test_df_fe.head())
    
    # Save the processed data
    train_df_fe.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/processed_train.csv', index=False)
    test_df_fe.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/processed_test.csv', index=False)
    
    print("Processed data saved successfully.")
    
    # Create Age*Class feature
    train_df_fe['Age*Class'] = train_df_fe['Age'] * train_df_fe['Pclass']
    test_df_fe['Age*Class'] = test_df_fe['Age'] * test_df_fe['Pclass']
    
    # Create FarePerPerson feature
    train_df_fe['FarePerPerson'] = train_df_fe['Fare'] / train_df_fe['FamilySize']
    test_df_fe['FarePerPerson'] = test_df_fe['Fare'] / test_df_fe['FamilySize']
    
    # Display the first few rows to verify the new features
    print("Training Data with Interaction Features:")
    print(train_df_fe.head())
    
    print("\nTest Data with Interaction Features:")
    print(test_df_fe.head())
    
    # Save the processed data
    train_df_fe.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/processed_train.csv', index=False)
    test_df_fe.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/processed_test.csv', index=False)
    
    print("Processed data saved successfully.")
    
    # Standardize numerical features
    scaler = StandardScaler()
    
    numerical_features = ['Age', 'Fare', 'FarePerPerson', 'Age*Class']
    train_df_fe[numerical_features] = scaler.fit_transform(train_df_fe[numerical_features])
    test_df_fe[numerical_features] = scaler.transform(test_df_fe[numerical_features])
    
    # Display the first few rows to verify the scaling
    print("Training Data with Scaled Features:")
    print(train_df_fe.head())
    
    print("\nTest Data with Scaled Features:")
    print(test_df_fe.head())
    
    # Save the processed data
    train_df_fe.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/processed_train.csv', index=False)
    test_df_fe.to_csv('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/processed_test.csv', index=False)
    
    print("Processed data saved successfully.")
    


if __name__ == "__main__":
    generated_code_function()