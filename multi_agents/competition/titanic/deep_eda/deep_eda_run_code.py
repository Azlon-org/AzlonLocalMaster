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
    print("Cleaned Training Data:")
    print(train_df.head())
    
    # Display the first few rows of the cleaned test data
    print("\nCleaned Test Data:")
    print(test_df.head())
    
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
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/deep_eda/images/survival_by_pclass.png')
    plt.close()
    
    # Visualize the relationship between 'Sex' and 'Survived'
    plt.figure(figsize=(8, 6))
    sns.countplot(x='Sex', hue='Survived', data=train_df)
    plt.title('Survival Count by Sex')
    plt.xlabel('Sex')
    plt.ylabel('Count')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/deep_eda/images/survival_by_sex.png')
    plt.close()
    
    # Visualize the relationship between 'Age' and 'Survived'
    plt.figure(figsize=(8, 6))
    sns.histplot(data=train_df, x='Age', hue='Survived', multiple='stack', kde=True)
    plt.title('Survival Distribution by Age')
    plt.xlabel('Age')
    plt.ylabel('Count')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/deep_eda/images/survival_by_age.png')
    plt.close()
    
    # Visualize the relationship between 'Fare' and 'Survived'
    plt.figure(figsize=(8, 6))
    sns.histplot(data=train_df, x='Fare', hue='Survived', multiple='stack', kde=True)
    plt.title('Survival Distribution by Fare')
    plt.xlabel('Fare')
    plt.ylabel('Count')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/deep_eda/images/survival_by_fare.png')
    plt.close()
    
    # Visualize the relationship between 'Embarked' and 'Survived'
    plt.figure(figsize=(8, 6))
    sns.countplot(x='Embarked', hue='Survived', data=train_df)
    plt.title('Survival Count by Embarked')
    plt.xlabel('Embarked')
    plt.ylabel('Count')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/deep_eda/images/survival_by_embarked.png')
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
        print(f"Chi-square test p-value for {feature}: {p_value}")
    
    # T-test for numerical variables
    def t_test(feature):
        survived = train_df[train_df['Survived'] == 1][feature]
        not_survived = train_df[train_df['Survived'] == 0][feature]
        t_stat, p = stats.ttest_ind(survived, not_survived, nan_policy='omit')
        return p
    
    numerical_features = ['Age', 'Fare']
    for feature in numerical_features:
        p_value = t_test(feature)
        print(f"T-test p-value for {feature}: {p_value}")
    
    # Correlation analysis
    numeric_columns = train_df.select_dtypes(include=['float64', 'int64']).columns
    correlation_matrix = train_df[numeric_columns].corr()
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/deep_eda/images/correlation_matrix.png')
    plt.close()
    
    # Visualize interaction between 'Pclass' and 'Sex' on 'Survived'
    plt.figure(figsize=(8, 6))
    sns.catplot(x='Pclass', hue='Sex', col='Survived', data=train_df, kind='count', height=5, aspect=1)
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/deep_eda/images/pclass_sex_survived.png')
    plt.close()
    
    # Visualize interaction between 'Pclass' and 'Embarked' on 'Survived'
    plt.figure(figsize=(8, 6))
    sns.catplot(x='Pclass', hue='Embarked', col='Survived', data=train_df, kind='count', height=5, aspect=1)
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/deep_eda/images/pclass_embarked_survived.png')
    plt.close()
    
    # Visualize interaction between 'Sex' and 'Embarked' on 'Survived'
    plt.figure(figsize=(8, 6))
    sns.catplot(x='Sex', hue='Embarked', col='Survived', data=train_df, kind='count', height=5, aspect=1)
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/deep_eda/images/sex_embarked_survived.png')
    plt.close()
    
    # Visualize interaction between 'SibSp' and 'Parch' on 'Survived'
    plt.figure(figsize=(8, 6))
    sns.catplot(x='SibSp', hue='Parch', col='Survived', data=train_df, kind='count', height=5, aspect=1)
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/deep_eda/images/sibsp_parch_survived.png')
    plt.close()
    


if __name__ == "__main__":
    generated_code_function()